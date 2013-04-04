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

import testbaserepo

import concrete_job
import installation_service

class ConcreteJobTest(testbaserepo.TestCase):
    def setUp(self):
        testbaserepo.TestCase.setUp(self)
        self.openRepository()
        for v in ["1", "2"]:
            self.addComponent("foo:runtime", v)
            self.addCollection("foo", v, [":runtime"])
            self.addCollection("group-bar", v, [ "foo" ])

        self.updatePkg(["group-bar=1"])

        self.systemModelPath = os.path.join(self.workDir, "system-model")
        file(self.systemModelPath, "w").write("install group-bar=2\n")

    def testPreviewSyncOperation(self):
        flags = installation_service.InstallationService.UpdateFlags()
        job = concrete_job.UpdateJob.previewSyncOperation(self.systemModelPath,
            flags)
        # Make sure system model got copied inside the job
        self.assertEquals(job.concreteJob.systemModel,
                file(self.systemModelPath).read())

    def testApplySyncOperation(self):
        flags = installation_service.InstallationService.UpdateFlags()
        job = concrete_job.UpdateJob.previewSyncOperation(self.systemModelPath,
            flags)

        jobId = job.get_job_id()

        job2 = concrete_job.UpdateJob.applySyncOperation(jobId, flags)

        # We reload the old job
        self.assertEquals(job2.get_job_id(), jobId)


