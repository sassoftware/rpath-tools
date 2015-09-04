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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
from conary import callbacks as conaryCallbacks
from conary.lib import util

from conary_test import rephelp

from testrunner import testcase
from testutils import mock
from rpath_tools.lib import clientfactory, installation_service, jobs, update


class TestCase(testcase.TestCaseWithWorkDir):
    def setUp(self):
        testcase.TestCaseWithWorkDir.setUp(self)

class TestCaseRepo(rephelp.RepositoryHelper):
    def setUp(self):
        rephelp.RepositoryHelper.setUp(self)
        self.openRepository()
        self._conaryClient = self.getConaryClient()
        util.mkdirChain(os.path.dirname(self._conaryClient.cfg.root + self._conaryClient.cfg.modelPath))
        self._conaryClient.setUpdateCallback(conaryCallbacks.UpdateCallback())

        # Create a Conary client that can talk to the testsuite repo
        class ConaryClientFactory(clientfactory.ConaryClientFactory):
            def getClient(slf, *args, **kwargs):
                return self._conaryClient
            def getCfg(slf, *args, **kwargs):
                return self._conaryClient.cfg

        self.mock(update.UpdateService, 'conaryClientFactory', ConaryClientFactory)
        self.storagePath = os.path.join(self.workDir, "storage")
        self.mock(installation_service.UpdateSet, "storagePath", self.storagePath)
        self.mock(jobs.BaseUpdateTask, "storagePath", self.storagePath)

    def tearDown(self):
        rephelp.RepositoryHelper.tearDown(self)
