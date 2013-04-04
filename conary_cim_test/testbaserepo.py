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
from conary_test import rephelp
from rpath_tools.lib import installation_service

import concrete_job
import testbase

class TestCase(rephelp.RepositoryHelper, testbase.ProviderMixIn):
    def setUp(self):
        rephelp.RepositoryHelper.setUp(self)
        self.openRepository()
        self._conaryClient = self.getConaryClient()
        self._conaryClient.setUpdateCallback(conaryCallbacks.UpdateCallback())

        # Create a Conary client that can talk to the testsuite repo
        class ConaryClientFactory(installation_service.ConaryClientFactory):
            def getClient(slf):
                return self._conaryClient

        installation_service.InstallationService.conaryClientFactory = ConaryClientFactory
        storagePath = os.path.join(self.workDir, "storage")
        self.mock(installation_service.UpdateSet, "storagePath", storagePath)
        self.mock(concrete_job.UpdateJob, "storagePath", storagePath)
        testbase.ProviderMixIn.setUp(self)

    def tearDown(self):
        rephelp.RepositoryHelper.tearDown(self)
        installation_service.InstallationService.conaryClientFactory = installation_service.ConaryClientFactory
        self.env = None

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
