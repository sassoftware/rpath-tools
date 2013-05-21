#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import logging
import os
import re
import subprocess
import time

from conary.lib import digestlib
from conary.lib import util

from rpath_tools.client import utils

logger = logging.getLogger(__name__)

class Uuid(object):
    def __init__(self, uuidFile=None):
        self.uuidFile = uuidFile
        self._uuid = None

    @property
    def uuid(self):
        if self._uuid is None:
            self._uuid = self.read()
        return self._uuid

    def read(self):
        return None

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
        uuid = self._generateUuid()
        if self.uuidFile:
            if not os.path.exists(self.uuidFile):
                uuid = self._generateUuid()
                self._writeFile(self.uuidFile, uuid)
            else:
                uuid = self._readFile(self.uuidFile)
        return uuid

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
        if not utils.runningInEC2():
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
            retuuid = GeneratedUuid.asString(sha.digest()[:16])
        else:
            dmidecodeUuid = self._getDmidecodeUuid().lower()
            retuuid = dmidecodeUuid

        if os.path.exists(self.uuidFile):
            persistedUuid = self._readFile(self.uuidFile)
            if persistedUuid.lower() != retuuid:
                self._writeDmidecodeUuid(retuuid)
        else:
            self._writeDmidecodeUuid(retuuid)

        return retuuid

    def _getUuidFromMac(self):
        """
        Use the mac address from the system to hash a uuid.
        """
        # Read mac address of self.deviceName
        if utils.runningInEC2():
            self.deviceName = 'eth0'

        mac = None

        if os.path.exists('/sys/class/net'):
            if not self.deviceName:
                deviceList = sorted( [ x for x in os.listdir('/sys/class/net') 
                                        if x != 'lo' ] )
                if deviceList:
                    self.deviceName = deviceList[0]

            mac = open('/sys/class/net/%s/address' % self.deviceName).read().strip()

        if not mac:
            # Legacy code
            if os.path.exists('/sbin/ifconfig'):
                logger.warn("No sysfs, falling back to ifconfig command.")
                cmd = ['/sbin/ifconfig']
                p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
                sts = p.wait()
                if sts != 0:
                    raise Exception("Unable to run ifconfig to find mac address"
                        " for local uuid generation")
                lines = p.stdout.read().strip()

                # Work around for empty deviceName bug 

                deviceList = None

                if not self.deviceName:
                    deviceList = sorted([ x.split()[0] for x in lines.split('\n')
                                        if 'lo' not in x and 'HWaddr' in x ])
                    if deviceList:
                        self.deviceName = deviceList[0]

                matcher = re.compile('^%s.*HWaddr\W(.*)$' % self.deviceName)

                for line in lines.split('\n'):
                    match = matcher.match(line)
                    if match:
                        mac = match.groups()[0].strip()

        if not mac:
            raise Exception("Unable to find mac address for "
                "local uuid generation")

        mac = mac.lower()

        if len(mac) > 16:
            mac = mac[-16:]
        elif len(mac) < 16:
            mac = mac + '0'*(16-len(mac))
        return self.asString(mac)

    def _getDmidecodeUuid(self):
        if not os.access("/dev/mem", os.R_OK):
            raise Exception("Must run as root")
        try:
            import dmidecode
        except ImportError:
            logger.warn("Can't import dmidecode, falling back to dmidecode command.")
            return self._getDmidecodeUuidCommand()

        try:
            return dmidecode.system()['0x0001']['data']['UUID']
        except Exception:
            # Depending on the target type, various Exceptions can be raised,
            # so just handle any exception.
            # kvm - AttributeError
            # xen - RuntimeError
            logger.warn("Can't use dmidecode library, falling back to mac address")
            return self._getUuidFromMac()

    def _getDmidecodeUuidCommand(self):
        try:
            dmidecode = "/usr/sbin/dmidecode"
            cmd = [ dmidecode, "-s", "system-uuid" ]
            p = subprocess.Popen(cmd, stdout = subprocess.PIPE)
            sts = p.wait()
            if sts != 0:
                raise Exception("Unable to extract system-uuid from dmidecode")
            uuid = p.stdout.readline().strip()
            if not uuid:
                raise Exception("Unable to extract system-uuid from dmidecode")
            return uuid
        except Exception:
            logger.warn("Can't use dmidecode command, falling back to mac address")
            return self._getUuidFromMac()

    def _writeDmidecodeUuid(self, uuid):
        destFilePath = os.path.join(self.oldDirPath, "%.1f" % time.time())
        self._writeFile(destFilePath, uuid)
        self._writeFile(self.uuidFile, uuid)



