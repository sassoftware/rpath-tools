#!/usr/bin/python
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

from rpath_toolstest.clienttest import RpathToolsTest


class ConfigTest(RpathToolsTest):

    def testReadFiles(self):
        pass

    def testGeneratedUuidFilePath(self):
        self.assertEquals(self.cfg.generatedUuidFilePath, 
                          os.path.join(self.cfg.topDir, 'generated-uuid'))

    def testLocalUuidFilePath(self):
        self.assertEquals(self.cfg.localUuidFilePath,
                          os.path.join(self.cfg.topDir, 'local-uuid'))

    def testLocalUuidOldDirectoryPath(self):
        self.assertEquals(self.cfg.localUuidOldDirectoryPath,
                          os.path.join(self.cfg.topDir, 'old-registrations'))

    def testLastPollFilePath(self):
        self.assertEquals(self.cfg.lastPollFilePath,
                          os.path.join(self.cfg.topDir, 'lastPoll'))

    def testDisableRegistrationFilePath(self):
        self.assertEquals(self.cfg.disableRegistrationFilePath,
                          os.path.join(self.cfg.topDir, 'disableRegistration'))

    def testLastRegistrationFilePath(self):
        self.assertEquals(self.cfg.lastRegistrationFilePath,
                          os.path.join(self.cfg.topDir, 'lastRegistration'))
