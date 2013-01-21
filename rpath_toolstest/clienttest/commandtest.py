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


import os
import time
import StringIO

from testutils import mock

from rpath_toolstest.clienttest import RpathToolsTest

from rpath_tools.client import register
from rpath_tools.client import command
from rpath_tools.client import hardware

class RpathToolsCommandTest(RpathToolsTest):

    commandClass = None

    def setUp(self):
        RpathToolsTest.setUp(self)
        self.command = self.commandClass()
        self.command.cfg = self.cfg

    def tearDown(self):
        mock.unmockAll()
        RpathToolsTest.tearDown(self)

class RegistrationCommandTest(RpathToolsCommandTest):

    commandClass = command.RegistrationCommand

    def setUp(self):
        RpathToolsCommandTest.setUp(self)
        self.command.check = False
        self.command.force = False
        self.command.boot = False
        self.command.shutdown = False
        self.command.event_uuid = None

    def testCheckRegistrationDisabled(self):
        # disable registration file does not exist on initial setup
        self.assertFalse(self.discardOutput(
            self.command.checkRegistrationDisabled))

        f = open(self.cfg.disableRegistrationFilePath, 'w')
        f.write('test')
        f.close()
        self.assertTrue(self.discardOutput(
            self.command.checkRegistrationDisabled))

    def _writeOldTimestamp(self, file, interval):
        f = open(file, 'w')
        ts = time.time() - 1 - interval * 24 * 60 * 60 
        f.write(str(ts))
        f.close()

    def _writeNewTimestamp(self, file):
        f = open(file, 'w')
        ts = time.time() 
        f.write(str(ts))
        f.close()

    def testCheckPollTimeout(self):
        # ts is older than the timeout
        self._writeOldTimestamp(self.cfg.lastPollFilePath,
                                self.cfg.contactTimeoutInterval)
        self.assertTrue(self.discardOutput(
            self.command.checkPollTimeout))

        # ts is newer than the timeout
        self._writeNewTimestamp(self.cfg.lastPollFilePath)
        self.assertFalse(self.discardOutput(
            self.command.checkPollTimeout))

    def testCheckRegistrationTimeout(self):
        # ts is older than the timeout
        self._writeOldTimestamp(self.cfg.lastRegistrationFilePath,
                                 self.cfg.registrationInterval)
        self.assertTrue(self.discardOutput(
            self.command.checkRegistrationTimeout))

        # ts is newer than the timeout
        self._writeNewTimestamp(self.cfg.lastRegistrationFilePath)
        self.assertFalse(self.discardOutput(
            self.command.checkRegistrationTimeout))

    def testShouldRun(self):
        self.assertTrue(self.discardOutput(self.command.shouldRun))

        self._writeOldTimestamp(self.cfg.lastPollFilePath,
                                self.cfg.contactTimeoutInterval)
        self.assertTrue(self.discardOutput(self.command.shouldRun))
        self._writeNewTimestamp(self.cfg.lastPollFilePath)

        self._writeOldTimestamp(self.cfg.lastRegistrationFilePath,
                                 self.cfg.registrationInterval)
        self.assertTrue(self.discardOutput(self.command.shouldRun))
        self._writeNewTimestamp(self.cfg.lastRegistrationFilePath)

        self._writeOldTimestamp(self.cfg.lastPollFilePath,
                                self.cfg.contactTimeoutInterval)
        self._writeOldTimestamp(self.cfg.lastRegistrationFilePath,
                                 self.cfg.registrationInterval)
        self.assertTrue(self.discardOutput(self.command.shouldRun))

        self.command.force = True
        self.assertTrue(self.discardOutput(self.command.shouldRun))
        self.command.force = False

        self.command.boot = True
        self.assertTrue(self.discardOutput(self.command.shouldRun))
        self.command.boot = False

        self.command.shutdown = True
        self.assertTrue(self.discardOutput(self.command.shouldRun))
        self.command.shutdown = False

    def testRunCommand(self):
        sslClientCertPath = os.path.join(self.testPath,
                                         'ssl_client_cert_path')
        f = open(sslClientCertPath, 'w')
        f.write('SSLCLIENTCERT')
        f.close()
        sslClientKeyPath = os.path.join(self.testPath,
                                        'ssl_client_key_path')
        f = open(sslClientKeyPath, 'w')
        f.write('SSLCLIENTKEY')
        f.close()
        sslCertificateFilePath = os.path.join(self.testPath,
                                        'ssl_certificate_file_path')
        f = open(sslCertificateFilePath, 'w')
        f.write('SSLSERVERCERT')
        f.close()

        mockRegistration = mock.MockObject()
        mockRegistration.readCredentials._mock.setDefaultReturn(
            (sslClientCertPath, sslClientKeyPath))
        mockRegistration._mock.set(
            sslCertificateFilePath=sslCertificateFilePath,
            generatedUuid='GENERATEDUUID',
            localUuid='LOCALUUID',
            sfcbConfig={},
            targetSystemId="target-system-id-007",
        )
        mockObj = mock.MockObject()
        mockObj._mock.origValue = register.Registration
        register.Registration = mockObj
        mock._mocked.append((register, 'Registration'))
        register.Registration._mock.setDefaultReturn(mockRegistration)

        IP = hardware.HardwareData.IP

        mockHardwareData = mock.MockObject()
        mockHardwareData.getIpAddresses._mock.setDefaultReturn([
            IP(ipv4='1.1.1.1', netmask='255.255.255.0', device='eth0',
                dns_name='host1.com',),
            IP(ipv4='2.2.2.2', netmask='255.255.0.0', device='eth1',
                dns_name='host2.com',),
            IP(ipv4='3.3.3.3', netmask='255.255.0.0', device='eth2',
                dns_name='host3.com',),
        ])
        mockHardwareData.getHostname._mock.setDefaultReturn('localhost.localdomain')
        mockHardwareData.getLocalIp._mock.setDefaultReturn('2.2.2.2')

        self.mock(hardware, 'HardwareData', mock.MockObject())
        hardware.HardwareData._mock.setDefaultReturn(mockHardwareData)

        self.cfg.requiredNetwork = '3.3.3.3'
        rc = self.discardOutput(self.command.runCommand, self.cfg,
            {'force':True, 'event-uuid' : 'uuid007', }, [])
        self.assertEquals(rc, 0)

        call = mockRegistration.registerSystem._mock.popCall()
        system = call[0][0]
        sio = StringIO.StringIO()
        system.serialize(sio)
        self.assertEquals('GENERATEDUUID', system.generated_uuid)
        self.assertEquals('LOCALUUID', system.local_uuid)
        self.assertEquals('SSLSERVERCERT', system.ssl_server_certificate)
        self.failUnlessEqual(system.event_uuid, 'uuid007')
        self.assertXMLEquals(sio.getvalue(), systemXmlAvailable)

        # Unset requiredNetwork, do not send an event uuid
        self.cfg.requiredNetwork = None
        rc = self.discardOutput(self.command.runCommand,
            self.cfg, {'force':True}, [])
        self.assertEquals(rc, 0)

        call = mockRegistration.registerSystem._mock.popCall()
        system = call[0][0]
        sio = StringIO.StringIO()
        system.serialize(sio)
        self.assertXMLEquals(sio.getvalue(),
            systemXmlAvailable.replace('<required>true</required>',
            '').replace('<event_uuid>uuid007</event_uuid', ''))

        # Test boot
        bootUuidFile = os.path.join(self.testPath, "boot-uuid")
        file(bootUuidFile, "w").write(" JeanValjean \n")
        self.mock(self.command, 'BOOT_UUID_FILE', bootUuidFile)
        rc = self.discardOutput(self.command.runCommand,
            self.cfg, dict(boot=True), [])
        self.assertEquals(rc, 0)

        call = mockRegistration.registerSystem._mock.popCall()
        system = call[0][0]
        sio = StringIO.StringIO()
        system.serialize(sio)
        self.assertXMLEquals(sio.getvalue(),
            systemXmlAvailable.replace('<required>true</required>',
            '').replace('<event_uuid>uuid007</event_uuid',
                '<boot_uuid>JeanValjean</boot_uuid>'))
        # The boot uuid file should be gone now
        self.failIf(os.path.exists(bootUuidFile))

class ConfigCommandTest(RpathToolsCommandTest):

    commandClass = command.ConfigCommand

    def setUp(self):
        RpathToolsCommandTest.setUp(self)

    def testRunCommand(self):
        rc, stdout = self.captureOutput(
                        self.command.runCommand, self.cfg, {}, [])
        # Replace the test tmp path in the config display with the
        # correct value from this test.
        cfgDisplay = configDisplay.replace('%TESTPATH%', self.testPath)
        self.assertEquals(cfgDisplay, stdout)

systemXmlAvailable = """\
<system>
    <generated_uuid>GENERATEDUUID</generated_uuid>
    <local_uuid>LOCALUUID</local_uuid>
    <ssl_server_certificate>SSLSERVERCERT</ssl_server_certificate>
    <hostname>localhost.localdomain</hostname>
    <current_state>
        <name>registered</name>
    </current_state>
    <target_system_id>target-system-id-007</target_system_id>
    <agent_port>5989</agent_port>
    <event_uuid>uuid007</event_uuid>
    <networks>
        <network>
            <ip_address>1.1.1.1</ip_address>
            <dns_name>host1.com</dns_name>
            <device_name>eth0</device_name>
            <netmask>255.255.255.0</netmask>
            <active>false</active>
        </network>
        <network>
            <ip_address>2.2.2.2</ip_address>
            <dns_name>host2.com</dns_name>
            <device_name>eth1</device_name>
            <netmask>255.255.0.0</netmask>
            <active>true</active>
        </network>
        <network>
            <ip_address>3.3.3.3</ip_address>
            <dns_name>host3.com</dns_name>
            <device_name>eth2</device_name>
            <netmask>255.255.0.0</netmask>
            <active>false</active>
            <required>true</required>
        </network>
    </networks>
    <management_interface>
      <name>cim</name>
    </management_interface>
</system>
"""

configDisplay = """\
bootRegistration          1
conaryProxyFilePath       /etc/conary/config.d/rpath-tools-conaryProxy
contactTimeoutInterval    3
debugMode                 False
directMethod              []
disableRegistrationFileName disableRegistration
generatedUuidFile         generated-uuid
lastPollFileName          lastPoll
lastRegistrationFileName  lastRegistration
localUuidBackupDirectoryName old-registrations
localUuidFile             local-uuid
logFile                   %TESTPATH%/log
randomWaitFileName        randomWait
randomWaitMax             14400
registrationInterval      1
registrationMethod        DIRECT
registrationPort          13579
registrationRetryCount    3
remoteCertificateAuthorityStore /etc/conary/rpath-tools/certs
retrySlotTime             15
scannerSurveyLockFile     /var/lock/subsys/survey
scannerSurveyStore        /var/lib/conary-cim/surveys
sfcbConfigurationFile     /etc/conary/sfcb/sfcb.cfg
sfcbUrl                   /tmp/sfcbHttpSocket
shutdownDeRegistration    1
slpMethod                 rpath-inventory
topDir                    %TESTPATH%
validateRemoteIdentity    True
"""
