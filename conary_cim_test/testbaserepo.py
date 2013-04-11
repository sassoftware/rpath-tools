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

from conary import callbacks as conaryCallbacks
from conary.lib import util
from conary_test import rephelp
from rpath_tools.lib import clientfactory, installation_service, update

from rpath_tools.lib import jobs

import testbase
from rpath_toolstest import testbase as rpath_tools_test

class TestCase(rpath_tools_test.TestCaseRepo, testbase.ProviderMixIn):
    def setUp(self):
        rpath_tools_test.TestCaseRepo.setUp(self)
        testbase.ProviderMixIn.setUp(self)

    def tearDown(self):
        testbase.ProviderMixIn.tearDown(self)
        rpath_tools_test.TestCaseRepo.tearDown(self)

    def waitJob(self, jobObjectPath, timeout = 1):
        jprov, _ = self.getProviderConcreteJob()
        # Iterate until state changes
        jobState = 0
        jobInst = None
        for i in range(int(timeout * 10)):
            jobInst = jprov.MI_getInstance(self.env, jobObjectPath, None)
            jobState = jobInst.properties['JobState'].value
            if jobState >= jprov.Values.JobState.Completed:
                return jobState, jobInst, jprov

            time.sleep(.1)
        return jobState, jobInst, jprov
