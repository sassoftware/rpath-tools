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

from rpath_tools.client import updater
from rpath_tools.lib import stored_objects

from .. import testbase


class UpdaterTest(testbase.TestCaseRepo):

    jobFactory = stored_objects.ConcreteUpdateJobFactory

    def setUp(self):
        testbase.TestCaseRepo.setUp(self)
        self.openRepository()
        for v in ["1", "2"]:
            self.addComponent("foo:runtime", v, fileContents=[
                ('/foo.txt', '123456789012345' + v),
            ])
            self.addCollection("foo", v, [":runtime"])
            self.addCollection("group-bar", v, [ "foo" ])

        self.updatePkg(["group-bar=1"])

        self.systemModelPath = os.path.join(self.workDir,
            "../root/etc/conary/system-model")

        file(self.systemModelPath, "w").write(
            "install group-bar=%s/1\n" % self.defLabel
        )

    def testEmptyPreview(self):
        up = updater.Updater()
        xml = up.preview(systemModel="install 'group-bar=%s/1'\n" % self.defLabel)
        tree = etree.fromstring(xml)
        jobId = tree.attrib["id"]
        downloadSize = tree.findtext("downloadSize")
        storagePath = os.path.join(self.storagePath, "jobs", jobId)
        self.assertEqual(int(downloadSize), 0)
        self.assertFalse(os.path.exists(storagePath))

    def testAppliedCleanUp(self):
        up = updater.Updater()
        xml = up.preview(systemModel="install 'group-bar=%s/2'\n" % self.defLabel)
        tree = etree.fromstring(xml)
        jobId = tree.attrib["id"]
        downloadSize = int(tree.findtext("downloadSize"))
        storagePath = os.path.join(self.storagePath, "jobs", jobId)
        self.assertTrue(downloadSize > 0)
        self.assertTrue(os.path.exists(storagePath))
        up.apply(jobId)
        self.assertFalse(os.path.exists(storagePath))
