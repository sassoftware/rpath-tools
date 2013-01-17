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
import tempfile

from testrunner import testhelp

from rpath_toolstest.clienttest import testsetup
from rpath_tools.client import config


class RpathToolsTest(testhelp.TestCase):

    def _setupConfig(self):
        self.cfg = config.RpathToolsConfiguration()
        self.cfg.topDir = self.testPath
        self.cfg.logFile = os.path.join(self.testPath, 'log')

    def setUp(self):
        testhelp.TestCase.setUp(self)
        self.testPath = tempfile.mkdtemp(prefix='rpath-tools-test-')
        self._setupConfig()
    
    def tearDown(self):
        testhelp.TestCase.tearDown(self)

if __name__ == "__main__":
        testsetup.main()
