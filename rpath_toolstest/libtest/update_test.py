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

from lxml import etree
import os

from rpath_toolstest import testbase

from rpath_tools.lib import stored_objects, update

class UpdateTest(testbase.TestCaseRepo):

    jobFactory = stored_objects.ConcreteUpdateJobFactory

    def setUp(self):
        testbase.TestCaseRepo.setUp(self)
        self.openRepository()
        for v in ["1", "2"]:
            self.addComponent("foo:runtime", v)
            self.addCollection("foo", v, [":runtime"])
            self.addCollection("group-bar", v, [ "foo" ])

        self.updatePkg(["group-bar=1"])

        self.systemModelPath = os.path.join(self.workDir, "system-model")
        file(self.systemModelPath, "w").write("install group-bar=2\n")

    def newJob(self):
        job = self.jobFactory(self.storagePath).new()
        job.state = "New"
        return job

    def loadJob(self, jobId):
        job = self.jobFactory(self.storagePath).load(jobId)
        return job

    def testSyncModelPreviewOperation(self):
        job = self.newJob()
        job.systemModel = file(self.systemModelPath).read()
        operation = update.SyncModel()
        preview = operation.preview(job)
        tree = etree.fromstring(preview)
        self.assertEquals(tree.attrib['id'], job.keyId)
        return job

    def testSyncModelApplyOperation(self):
        job = self.testSyncModelPreviewOperation()
        job_test = self.loadJob(job.keyId)

        operation = update.SyncModel()
        preview = operation.apply(job_test)
        tree = etree.fromstring(preview)
        self.assertEquals(tree.attrib['id'], job.keyId)
        return job

    def testFreezeUpdateJob(self):
        pass

    def testThawUpdateJob(self):
        pass

    def testReadSystemModel(self):
        pass

    def testUpdateModel(self):
        pass

    def testUpdateModelFromString(self):
        pass

    def testTopLevelItems(self):
        pass



