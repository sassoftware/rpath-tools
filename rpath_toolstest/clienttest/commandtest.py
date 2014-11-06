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

import difflib

from testutils import mock
from rpath_toolstest.clienttest import RpathToolsTest
from rpath_tools.client import command


configDisplay = """\
bootRegistration          0
bootUuidFile              boot-uuid
conaryProxyFilePath       /etc/conary/config.d/rpath-tools-conaryProxy
contactTimeoutInterval    0
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
registrationInterval      0
registrationMethod        DIRECT
registrationPort          13579
registrationRetryCount    3
remoteCertificateAuthorityStore /etc/conary/rpath-tools/certs
retrySlotTime             15
scannerSurveyLockFile     /var/lock/subsys/survey
scannerSurveyStore        /var/lib/conary-cim/surveys
sfcbConfigurationFile     /etc/conary/sfcb/sfcb.cfg
sfcbUrl                   /tmp/sfcbHttpSocket
shutdownDeRegistration    0
slpMethod                 rpath-inventory
topDir                    %TESTPATH%
validateRemoteIdentity    True
"""


class RpathToolsCommandTest(RpathToolsTest):

    commandClass = None

    def setUp(self):
        RpathToolsTest.setUp(self)
        self.command = self.commandClass()
        self.command.cfg = self.cfg

    def tearDown(self):
        mock.unmockAll()
        RpathToolsTest.tearDown(self)


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
        try:
            self.assertEquals(cfgDisplay, stdout)
        except AssertionError as e:
            raise AssertionError(e.message + '\n'.join(difflib.unified_diff(
                cfgDisplay.split('\n'),
                stdout.split('\n'),
            )))
