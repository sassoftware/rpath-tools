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
import os.path
import pwd
import re
import subprocess
import sys
import tempfile
import time

from conary import conarycfg
from conary.lib import digestlib
from conary.lib import util

from rpath_tools.client import config
from rpath_tools.client import errors
from rpath_tools.client import utils
from rpath_tools.client.utils import x509

logger = logging.getLogger('client')

def main():
    cfg = config.RpathToolsConfiguration()
    cfg.topDir = '/etc/conary'
    r = Registration(cfg)
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

    @classmethod
    def asString(cls, data):
        """Generate a UUID out of the data"""
        assert len(data) == 16
        h = "%02x"
        fmt = '-'.join([h * 4, h * 2, h * 2, h * 2, h * 6])
        return fmt % tuple(ord(x) for x in data)

class GeneratedUuid(Uuid):
    def read(self):
        if not os.path.exists(self.uuidFile):
            uuid = self._generateUuid()
            self._writeFile(self.uuidFile, uuid)
        else:
            uuid = self._readFile(self.uuidFile)
        self._uuid = uuid

    @classmethod
    def _generateUuid(cls):
        data = file("/dev/urandom").read(16)
        return cls.asString(data)

class LocalUuid(Uuid):
    def __init__(self, uuidFile, oldDir, deviceName=None):
        self.oldDirPath = os.path.join(os.path.dirname(uuidFile), oldDir)
        Uuid.__init__(self, uuidFile)
        self._targetSystemId = None
        self.deviceName = deviceName

    @classmethod
    def _readProcVersion(cls):
        try:
            version = file("/proc/version").read()
        except IOError:
            return None
        return version

    @classmethod
    def _readInstanceIdFromEC2(cls):
        try:
            from amiconfig import instancedata
        except ImportError:
            return None
        return instancedata.InstanceData().getInstanceId()

    @classmethod
    def _getEC2InstanceId(cls):
        """
        Return the EC2 instance ID if the system is running in EC2
        Return None otherwise.
        """
        version = cls._readProcVersion()
        if version is None:
            return None
        if not ('amazon' in version or 'aes' in version or 'SAST' in version):
            return None
        return cls._readInstanceIdFromEC2()

    @property
    def ec2InstanceId(self):
        if self._targetSystemId is None:
            self._targetSystemId = self._getEC2InstanceId()
        return self._targetSystemId

    @property
    def targetSystemId(self):
        return self.ec2InstanceId

    def read(self):
        instanceId = self.ec2InstanceId
        if instanceId is not None:
            sha = digestlib.sha1(instanceId)
            self._uuid = GeneratedUuid.asString(sha.digest()[:16])
        else:
            dmidecodeUuid = self._getDmidecodeUuid().lower()
            self._uuid = dmidecodeUuid

        if os.path.exists(self.uuidFile):
            persistedUuid = self._readFile(self.uuidFile)
            if persistedUuid.lower() != self._uuid:
                self._writeDmidecodeUuid(self._uuid)
        else:
            self._writeDmidecodeUuid(self._uuid)

    
    def _getUuidFromMac(self):
        """
        Use the uuidgen command to generate a uuid based on the current time
        and the system's ethernet hardware address.
        """
        # Read mac address of self.deviceName
        cmd = ['/sbin/ifconfig']
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        sts = p.wait()
        if sts != 0:
            raise Exception("Unable to run ifconfig to find mac address for "
                "local uuid generation")
        lines = p.stdout.readline().strip()
        matcher = re.compile('^%s.*HWaddr\W(.*)$' % self.deviceName)
        for line in lines.split('\n'):
            match = matcher.match(line)
            if match:
                mac = match.groups()[0]

        if len(mac) > 16:
            mac = mac[0:16]
        elif len(mac) < 16:
            mac = mac + '0'*(16-len(mac))
        return self.asString(mac)

    def _getDmidecodeUuid(cls):
        if not os.access("/dev/mem", os.R_OK):
            raise Exception("Must run as root")
        try:
            import dmidecode
            return dmidecode.system()['0x0001']['data']['UUID']
        except ImportError:
            # python-dmidecode not present
            pass
        except KeyError:
            # dmidecode does not expose UUID in kvm
            return self._getUuidFromMac()

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

    def __init__(self, cfg, deviceName=None):
        self.cfg = cfg
        self.generatedUuid = GeneratedUuid(self.cfg.generatedUuidFilePath).uuid
        localUuidObj = LocalUuid(self.cfg.localUuidFilePath,
                                 self.cfg.localUuidOldDirectoryPath,
                                 deviceName)
        self.localUuid = localUuidObj.uuid
        self.targetSystemId = localUuidObj.targetSystemId
        self._sfcbCfg = None

        self.registrationMethods = {'DIRECT' : self.registerDirect,
                                  'SLP'    : self.registerSLP}

    @classmethod
    def registration(self, cfg=None):
        if not cfg:
            cfg = config.RpathToolsConfiguration()
        return Registration(cfg)

    def writeCertificate(self, crt):
        sfcbClientTrustStore = self.sfcbConfig.get('sslClientTrustStore',
            '/etc/conary/sfcb/clients')
        if self.sfcbConfig.get('httpUserSFCB', 'true'):
            sfcbHttpUser = self.sfcbConfig.get('httpUser', 'root')
        else:
            sfcbHttpUser = 'root'
        if sfcbHttpUser != 'root':
            uid, gid = self._getUserIds(sfcbHttpUser)
        else:
            uid, gid = None, None
        self.writeCertificateToStore(crt, sfcbClientTrustStore, uid=uid,
            gid=gid)
        # Remove this cert's issuer from the store
        #self.removeIssuerFromStore(crt, sfcbClientTrustStore)

    def writeCertificateToStore(self, crt, store, uid=None, gid=None):
        """
        Write the certifcate to the store, using the supplied uid and gid
        """
        certHash = crt.hash
        x509Pem = crt.x509.as_pem()
        certPath = self._getPathInCertificateStore(store, certHash, x509Pem)

        if certPath is None:
            # Already written
            return None
        logger.info("Writing certificate as %s" % certPath)
        util.mkdirChain(os.path.dirname(certPath))
        f = util.AtomicFile(certPath, chmod=0600)
        f.write(x509Pem)
        f.commit()
        if uid or gid:
            os.chown(certPath, uid, gid)
        return certPath

    def writeConaryProxy(self, remote):
        """
        Management nodes should already be written as conaryProxies by the cim
        interface, but add an extra check here to be sure.
        """
        conaryCfg = conarycfg.ConaryConfiguration(readConfigFiles=True)
        proxy = 'https://%s' % remote.split(':')[0]
        if proxy not in conaryCfg.conaryProxy.values():
            f = open(self.cfg.conaryProxyFilePath, 'wa')
            logger.info("Writing %s as a conary proxy to %s" % \
                (proxy, self.cfg.conaryProxyFilePath))
            f.write('conaryProxy %s\n' % proxy)
            f.close()

    def removeIssuerFromStore(self, crt, store):
        certHash = crt.hash
        issuerHash = crt.hash_issuer
        if certHash == issuerHash:
            # Self-signed cert
            return False
        destPath = os.path.join(store, "%s.%d" % (issuerHash, 0))
        util.removeIfExists(destPath)
        return True

    def _getPathInCertificateStore(self, store, certHash, x509Pem):
        for i in range(5):
            destPath = os.path.join(store, "%s.%d" % (certHash, i))
            if not os.path.exists(destPath):
                return destPath
            # Same contents?
            if file(destPath).read().strip() == x509Pem.strip():
                return None
            # Different cert, save it as a different file
        # We really shouldn't hit this
        raise Exception("Unable to write certificate to store")

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

    def getRemote(self):
        remote = []
        for method in self.cfg.registrationMethod:
            if method.upper() == 'DIRECT':
                remote = [r for r in self.cfg.directMethod]
            elif method.upper() == 'SLP':
                remote += self.getSlpRemote()
        return remote

    def getSlpRemote(self):
        remote = []
        for service in self.cfg.slpMethod:
            slptool = subprocess.Popen(['/usr/bin/slptool', 'findsrvs', 
                                        'service:%s' % service],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdoutData, stderrData = slptool.communicate()
            if stdoutData:
                remote.append(
                    stdoutData.strip('service:%s//' % service).split(',')[0])
        return remote

    def registerSystem(self, system):
        sio = StringIO.StringIO()
        system.serialize(sio)
        systemXml = sio.getvalue()
        for method in self.cfg.registrationMethod:
            func = self.registrationMethods.get(method.upper(), None)

            if not func:
                msg = 'Invalid registration method "%s". Check the activationMethod configuration parameter ' % method
                logger.error(msg)
                raise errors.RpathToolsError(msg)

            registered = func(systemXml)
            # If we registered successfully, there is no need to try other
            # methods.
            if registered:
                self.updateRegistrationFile()
                return True

        print '  Registration failed.  Check the log file at %s' % \
            self.cfg.logFile
        return False
                
    def registerDirect(self, systemXml):
        logger.info("Using Direct registration.")
        actResp = None
        for remote in self.cfg.directMethod:
            remote = remote.strip()
            if not remote:
                # Simetimes we see the empty string being passed in. Ignore it
                continue
            actResp = self._register(remote, systemXml)
            if actResp:
                break

        return actResp

    def registerSLP(self, systemXml):
        logger.info("Using SLP registration.")
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
        system = self._register_system(remote, systemXml)
        if system is None:
            return system
        # If the server returned something back, save the client cert
        if not system.ssl_client_certificate:
            return system
        crt = x509.X509(None, None)
        crt.load_x509(system.ssl_client_certificate)
        self.writeCertificate(crt)
        self.writeConaryProxy(remote)
        return system

    def _getRegistrationClient(self, remote):
        SSL = utils.client.SSL
        ssl_context = SSL.Context()
        if self.cfg.validateRemoteIdentity:
            ssl_context.load_verify_locations(
                capath=self.cfg.remoteCertificateAuthorityStore)
            ssl_context.set_allow_unknown_ca(False)
            ssl_context.set_verify(SSL.verify_peer, True)

        regClient = utils.client.RegistrationClient(remote,
            ssl_context=ssl_context)
        return regClient

    def _register_system(self, remote, systemXml):
        logger.info('Attempting registration with %s' % remote)
        print '  Attempting registration with %s...' % remote,

        regClient = self._getRegistrationClient(remote)
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
            registered = regClient.register(systemXml)

            if registered:
                logger.info('Registration with %s succesful' % remote)
                print "successful."
                return regClient.system
            print "failed."
            logger.info('Registration with %s failed.' % remote)
            sleepInc = (self.cfg.retrySlotTime * 2**attempts) - sleepTime
            randSleepInc = random.random() * sleepInc
            sleepTime = sleepTime + int(randSleepInc)
            attempts += 1
        return None

if __name__ == '__main__':
    sys.exit(main())
