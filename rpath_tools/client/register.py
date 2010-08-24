#
# Copyright (c) 2010 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#


import StringIO
import logging
import random
import os
import pwd
import subprocess
import sys
import tempfile
import time

from M2Crypto.SSL.Checker import SSLVerificationError

from conary.lib import util

from rpath_tools.client import config
from rpath_tools.client import errors
from rpath_tools.client.utils import client
from rpath_tools.client.utils import x509

logger = logging.getLogger('registration')

def main():
    cfg = config.rRegisterConfiguration()
    cfg.topDir = '/etc/conary'
    r = Registration(cfg)
    r.readCredentials()
    return r.generatedUuid, r.localUuid


class Uuid(object):
    def __init__(self, uuidFile=None):
        self.uuidFile = uuidFile
        self._uuid = None

    @property
    def uuid(self):
        if self._uuid is None:
            self.read()
        return self._uuid

    def read(self):
        pass

    def _readFile(cls, path):
        return file(path).readline().strip()

    def _writeFile(cls, path, contents):
        util.mkdirChain(os.path.dirname(path))
        file(path, "w").write(contents)


class GeneratedUuid(Uuid):
    def read(self):
        if not os.path.exists(self.uuidFile):
            uuid = self._generateUuid()
            self._writeFile(self.uuidFile, uuid)
        else:
            uuid = self._readFile(self.uuidFile)
        self._uuid = uuid

    def _generateUuid(cls):
        data = file("/dev/urandom").read(16)
        h = "%02x"
        fmt = '-'.join([h * 4, h * 2, h * 2, h * 2, h * 6])
        return fmt % tuple(ord(x) for x in data)


class LocalUuid(Uuid):
    def __init__(self, uuidFile, oldDir):
        self.oldDirPath = os.path.join(os.path.dirname(uuidFile), oldDir)
        Uuid.__init__(self, uuidFile)

    def read(self):
        dmidecodeUuid = self._getDmidecodeUuid().lower()
        self._uuid = dmidecodeUuid

        if os.path.exists(self.uuidFile):
            persistedUuid = self._readFile(self.uuidFile)
            if persistedUuid.lower() != dmidecodeUuid:
                self._writeDmidecodeUuid(dmidecodeUuid)
        else:
            self._writeDmidecodeUuid(dmidecodeUuid)

    def _getDmidecodeUuid(cls):
        if not os.access("/dev/mem", os.R_OK):
            raise Exception("Must run as root")
        try:
            import dmidecode
            return dmidecode.system()['0x0001']['data']['UUID']
        except ImportError:
            # python-dmidecode not present
            pass
        dmidecode = "/usr/sbin/dmidecode"
        # XXX if dmidecode is not present, make something up
        cmd = [ dmidecode, "-s", "system-uuid" ]
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        sts = p.wait()
        if sts != 0:
            raise Exception("Unable to extract system-uuid from dmidecode")
        uuid = p.stdout.readline().strip()
        return uuid

    def _writeDmidecodeUuid(self, uuid):
        destFilePath = os.path.join(self.oldDirPath, "%.1f" % time.time())
        self._writeFile(destFilePath, uuid)
        self._writeFile(self.uuidFile, uuid)


class Registration(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.generatedUuid = GeneratedUuid(self.cfg.generatedUuidFilePath).uuid
        self.localUuid = LocalUuid(self.cfg.localUuidFilePath, 
                                   self.cfg.localUuidOldDirectoryPath).uuid
        self._sfcbCfg = None

        self.registrationMethods = {'DIRECT' : self.registerDirect,
                                  'SLP'    : self.registerSLP}

    @classmethod
    def registration(self, cfg=None):
        if not cfg:
            cfg = config.RpathToolsConfiguration()
        return Registration(cfg)

    def readCredentials(self):
        if os.path.exists(self.cfg.credentialsCertFilePath):
            return (self.cfg.credentialsCertFilePath,
                self.cfg.credentialsKeyFilePath)
        # Generate credentials
        cn = "Common name for %s" % self.generatedUuid
        certDir = os.path.dirname(self.cfg.credentialsCertFilePath)
        util.mkdirChain(certDir)
        certFile, keyFile = x509.X509.new(cn, certDir)

        sfcbClientTrustStore = self.sfcbConfig.get('sslClientTrustStore',
            '/etc/conary/sfcb/clients')
        # Copy the public key to sfcb's directory
        util.copyfile([ certFile ], sfcbClientTrustStore)

        if self.sfcbConfig.get('httpUserSFCB', 'true'):
            sfcbHttpUser = self.sfcbConfig.get('httpUser', 'root')
        else:
            sfcbHttpUser = 'root'
        if sfcbHttpUser != 'root':
            uid, gid = self._getUserIds(sfcbHttpUser)
            path = os.path.join(sfcbClientTrustStore,
                                os.path.basename(certFile))
            os.chown(path, uid, gid)

        os.symlink(os.path.basename(certFile),
            self.cfg.credentialsCertFilePath)
        os.symlink(os.path.basename(keyFile), self.cfg.credentialsKeyFilePath)

        return (self.cfg.credentialsCertFilePath,
            self.cfg.credentialsKeyFilePath)

    @property
    def sslCertificateFilePath(self):
        return self.sfcbConfig.get('sslCertificateFilePath',
            '/etc/conary/sfcb/server.pem')

    @property
    def sfcbConfig(self):
        if self._sfcbCfg is None:
            self._sfcbCfg = self.parseSfcbCfg()
        return self._sfcbCfg

    def parseSfcbCfg(self):
        sfcbFilePath = self.cfg.sfcbConfigurationFile
        try:
            f = file(sfcbFilePath)
        except IOError:
            return {}
        # Get rid of all comments and empty lines
        lines = (x.strip() for x in f)
        lines = (x for x in lines if x and not x.startswith('#'))
        cfgVals = (x.split(':', 1) for x in lines)
        cfgVals = (x for x in cfgVals if len(x) == 2)
        return dict((x.strip(), y.strip()) for (x, y) in cfgVals)

    @classmethod
    def _getUserIds(cls, user):
        try:
            strct = pwd.getpwnam(user)
            return strct.pw_uid, strct.pw_gid
        except KeyError:
            return (0, 0)

    def updateRegistrationFile(self):
        now = time.time()
        logger.debug('Updating registration file timestamp to %s' % now)
        f = open(self.cfg.lastRegistrationFilePath, 'w')
        f.write(str(now))

    def registerSystem(self, system):
        sio = StringIO.StringIO()
        system.export(sio, 0, namespace_='', name_='system')
        systemXml = sio.getvalue()
        for method in self.cfg.registrationMethod:
            func = self.registrationMethods.get(method.upper(), None)

            if not func:
                msg = 'Invalid registration method "%s". Check the activationMethod configuration parameter ' % method
                logger.error(msg)
                raise errors.rRegisterError(msg)

            registerd = func(systemXml)
            # If we registerd successfully, there is no need to try other
            # methods.
            if registerd:
                self.updateRegistrationFile()
                return True

        print '  Registration failed.  Check the log file at %s' % \
            self.cfg.logFile
        return False
                
    def registerDirect(self, systemXml):
        logger.info("Using Direct registration.")
        actResp = None
        for remote in self.cfg.directMethod:
            actResp = self._register(remote, systemXml)
            if actResp:
                break

        return actResp

    def registerSLP(self, systemXml):
        logger.info("Using SLP registration.")
        import subprocess 
        actResp = None
        for service in self.cfg.slpMethod:
            logger.info('Searching for "%s" SLP service.' % service)
            slptool = subprocess.Popen(['/usr/bin/slptool', 'findsrvs', 
                                        'service:%s' % service],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdoutData, stderrData = slptool.communicate()
            if stdoutData:
                remote = stdoutData.strip('service:%s//' % service).split(',')[0]
                logger.info('"%s" SLP service found at %s' % (service, remote))
            else:
                logger.info('No "%s" SLP service found.' % service)
                continue

            actResp = self._register(remote, systemXml)

            if actResp:
                break

        return actResp

    def _register(self, remote, systemXml):
        logger.info('Attempting registration with %s' % remote)
        print '  Attempting registration with %s...' % remote,

        if self.cfg.validateRemoteIdentity and not self._validate(remote):
            return None

        actClient = client.RegistrationClient(remote)
        sleepTime = 0
        attempts = 0

        while attempts < self.cfg.registrationRetryCount:
            if attempts > 0:
                logger.info('Retrying registration attempt with %s' % remote)
            if sleepTime > 0:
                logger.info('Sleeping for %s seconds...' % sleepTime)
                time.sleep(sleepTime)

            logger.debug('Registration attempt %s with %s' % \
                         (attempts, remote))
            response = actClient.register(systemXml)

            if response:
                logger.info('Registration with %s succesful' % remote)
                print "successful."
                return response
                break
            else:
                print "failed."
                logger.info('Registration with %s failed.' % remote)
                sleepInc = (self.cfg.retrySlotTime * 2**attempts) - sleepTime
                randSleepInc = random.random() * sleepInc
                sleepTime = sleepTime + int(randSleepInc)
                attempts += 1

    def _validate(self, remote):
        logger.info("Validating identity of %s..." % remote)
        try:
            x509.X509.verify(self.cfg.remoteCAFilePath, remote) 
        except SSLVerificationError, e:
            logger.error("%s failed identity validation!" % remote)
            logger.error(str(e))
            return False
        except Exception, e:
            logger.error("Unknown error ocurred during identity validation "
                         "of %s" % remote)
            logger.error(str(e))
            return False

        return True

if __name__ == '__main__':
    sys.exit(main())
