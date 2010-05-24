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


import logging
import random
import os
import pwd
import subprocess
import sys
import time
import StringIO

from conary.lib import util

from ractivate import config
from ractivate import errors
from ractivate.utils import client
from ractivate.utils import x509

logger = logging.getLogger('activation')

def main():
    cfg = config.rActivateConfiguration()
    cfg.topDir = '/etc/conary'
    r = Activation(cfg)
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
        pid, sts = os.waitpid(p.pid, 0)
        uuid = p.stdout.readline().strip()
        return uuid

    def _writeDmidecodeUuid(self, uuid):
        destFilePath = os.path.join(self.oldDirPath, "%.1f" % time.time())
        self._writeFile(destFilePath, uuid)
        self._writeFile(self.uuidFile, uuid)


class Activation(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.generatedUuid = GeneratedUuid(self.cfg.generatedUuidFilePath).uuid
        self.localUuid = LocalUuid(self.cfg.localUuidFilePath, 
                                   self.cfg.localUuidOldDirectoryPath).uuid
        self._sfcbCfg = None

        self.activationMethods = {'DIRECT' : self.activateDirect,
                                  'SLP'    : self.activateSLP}

    @classmethod
    def activation(self, cfg=None):
        if not cfg:
            cfg = config.rActivateConfiguration()
        return Activation(cfg)

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
            '/etc/sfcb/conary/clients')
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

    def updateActivationFile(self):
        now = time.time()
        logger.debug('Updating activation file timestamp to %s' % now)
        f = open(self.cfg.lastActivationFilePath, 'w')
        f.write(str(now))

    def activateSystem(self, system):
        sio = StringIO.StringIO()
        system.export(sio, 0, namespace_='', name_='system')
        systemXml = sio.getvalue()
        for method in self.cfg.activationMethod:
            func = self.activationMethods.get(method.upper(), None)

            if not func:
                msg = 'Invalid activation method "%s". Check the activationMethod configuration parameter ' % method
                logger.error(msg)
                raise errors.rActivateError(msg)

            activated = func(systemXml)
            # If we activated successfully, there is no need to try other
            # methods.
            if activated:
                self.updateActivationFile()
                return
                
    def activateDirect(self, systemXml):
        logger.info("Using Direct activation.")
        for remote in self.cfg.directMethod:
            actResp = self._activate(remote, systemXml)
            if actResp:
                break

        return actResp

    def activateSLP(self, systemXml):
        logger.info("Using SLP activation.")
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

            actResp = self._activate(remote, systemXml)

            if actResp:
                break

        return actResp

    def _activate(self, remote, systemXml):
        logger.info('Attempting activation with %s' % remote)
        actClient = client.ActivationClient(remote)
        sleepTime = 0
        attempts = 0

        while attempts < self.cfg.activationRetryCount:
            if attempts > 0:
                logger.info('Retrying activation attempt with %s' % remote)
            if sleepTime > 0:
                logger.info('Sleeping for %s seconds...' % sleepTime)
                time.sleep(sleepTime)

            logger.debug('Activation attempt %s with %s' % \
                         (attempts, remote))
            response = actClient.activate(systemXml)

            # TODO: validate the response to make sure we activated correctly.
            if response:
                logger.info('Activation with %s succesful' % remote)
                return response
                break
            else:
                logger.info('Activation with %s failed.' % remote)
                sleepInc = (self.cfg.retrySlotTime * 2**attempts) - sleepTime
                randSleepInc = random.random() * sleepInc
                sleepTime = sleepTime + int(randSleepInc)
                attempts += 1

if __name__ == '__main__':
    sys.exit(main())
