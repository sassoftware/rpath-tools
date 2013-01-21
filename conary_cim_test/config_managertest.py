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
import sys
import time

from conary.lib import util

import testbase
import logging

import config_manager
import cim_logger

class ConfigTestMixin(object):
    def setUp(self):
        self.binaryPath = os.path.join(self.workDir, "executable")

        self.mock(config_manager.ConfigManager, 'ConfigFilePath',
            os.path.join(self.workDir, "values.xml"))
        self.mock(config_manager.ConfigManager, 'BinaryPath', self.binaryPath)
        self.logFile = os.path.join(self.workDir, "conary-cim.log")
        self.logger = cim_logger.Logger('testsuite', self.logFile)

    def setBinary(self, failed=False):
        retval = int(failed)
        file(self.binaryPath, "w").write("""\
#!/bin/bash

if [ %(retval)s -eq 0 ]; then
    echo $@
else
    echo $@ >&2
fi
exit %(retval)s
""" % dict(retval=retval))
        os.chmod(self.binaryPath, 0755)


class ConfigManagerTest(testbase.TestCase, ConfigTestMixin):
    def setUp(self):
        testbase.TestCase.setUp(self)
        ConfigTestMixin.setUp(self)

    def testIterConfigurations(self):
        cm = config_manager.ConfigManager(self.logger)
        configs = [ x for x in cm.iterConfigurations() ]
        self.failUnlessEqual([ x.path for x in configs ],
            [ os.path.join(self.workDir, 'values.xml') ])
        self.failUnlessEqual([ x.value for x in configs ],
            [ None ])

        config = configs[0]
        self.failUnlessEqual(config.value, None)
        self.failIf(os.path.exists(config.path))

        config.value = 'abc'
        self.failUnlessEqual(config.value, 'abc')
        self.failUnless(os.path.exists(config.path))

    def testApply(self):
        cm = config_manager.ConfigManager(self.logger)
        config = cm.iterConfigurations().next()

        self.setBinary(failed=False)
        retcode, stdout, stderr = cm.apply(config)
        self.failUnlessEqual(retcode, 0)
        self.failUnlessEqual(stdout, "-x %s\n" %
            config_manager.ConfigManager.ConfigFilePath)

        self.setBinary(failed=True)
        retcode, stdout, stderr = cm.apply(config)
        self.failUnlessEqual(retcode, 1)
        self.failUnlessEqual(stderr, "-x %s\n" %
            config_manager.ConfigManager.ConfigFilePath)
