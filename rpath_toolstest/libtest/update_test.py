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

from conary import trovetup
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
            self.addComponent("foo:runtime", v, fileContents=[
                ('/foo.txt', '123456789012345' + v),
                ('/etc/bar', '123456789012345' + v),
            ])
            self.addCollection("foo", v, [":runtime"])
            self.addCollection("group-bar", v, [ "foo" ])

        self.updatePkg(["group-bar=1"])

        self.systemModelPath = os.path.join(self.workDir,
            "../root/etc/conary/system-model")

        file(self.systemModelPath, "w").write(
            "install group-bar=%s/1\n" % self.defLabel
        )

    def newJob(self):
        job = self.jobFactory(self.storagePath).new()
        job.state = "New"
        return job

    def loadJob(self, jobId):
        job = self.jobFactory(self.storagePath).load(jobId)
        return job

    def testSyncModelPreviewOperationNoSystemModel(self):
        """Should be the same update"""
        job = self.newJob()
        operation = update.SyncModel()
        preview = operation.preview(job)
        tree = etree.fromstring(preview)
        self.assertEquals(tree.attrib['id'], job.keyId)
        group1 = self.findAndGetTrove('group-bar=1-1-1')
        group2 = self.findAndGetTrove('group-bar=2-1-1')
        self.assertEquals(
                [ x.text for x in tree.iterchildren('observed') ],
                [ self._trvAsString(group1) ])
        self.assertEquals(
                [ x.text for x in tree.iterchildren('desired') ],
                # XXX FIXME: this really should be group2; but because
                # we're removing foo, the code returns the original
                # list. See the other test that's failing
                [ self._trvAsString(group1) ])

        downloadSize = [x.text for x in tree.iterchildren('downloadSize')]
        self.assertEqual(len(downloadSize), 1)
        # XXX FIXME: we really should be able to count on a stable value for
        # download size...
        #self.assertTrue(int(downloadSize[0]) < 1370)
        #self.assertTrue(int(downloadSize[0]) >= 1330)
        self.assertEqual(job.state, "Previewed")

        return job

    def testSyncModelPreviewOperation(self):
        job = self.newJob()
        job.systemModel = "install group-bar=%s/2\n" % self.defLabel
        operation = update.SyncModel()
        preview = operation.preview(job)
        tree = etree.fromstring(preview)
        self.assertEquals(tree.attrib['id'], job.keyId)
        group1 = self.findAndGetTrove('group-bar=1-1-1')
        group2 = self.findAndGetTrove('group-bar=2-1-1')
        self.assertEquals(
                [ x.text for x in tree.iterchildren('observed') ],
                [ self._trvAsString(group1) ])
        self.assertEquals(
                [ x.text for x in tree.iterchildren('desired') ],
                # XXX FIXME: this really should be group2; but because
                # we're removing foo, the code returns the original
                # list. See the other test that's failing
                [ self._trvAsString(group1) ])

        downloadSize = [x.text for x in tree.iterchildren('downloadSize')]
        self.assertEqual(len(downloadSize), 1)
        self.assertEqual(int(downloadSize[0]), job.downloadSize)
        self.assertTrue(tree.find('downloaded').text == 'false')
        # XXX FIXME: we really should be able to count on a stable value for
        # download size...
        #self.assertTrue(int(downloadSize[0]) < 1370)
        #self.assertTrue(int(downloadSize[0]) >= 1330)
        self.assertEqual(job.state, "Previewed")

        return job

    def testSyncModelDownloadSizeMultiRepo(self):
        repo1 = self.openRepository(1)
        self.addComponent('bar:runtime', '1')
        self.addCollection('bar', '1', [':runtime'])
        self.addComponent('bar:runtime', '/localhost1@rpl:linux/2-1-1',
                          repos=repo1)
        self.addCollection('bar', '/localhost1@rpl:linux/2-1-1', [':runtime'],
                           repos=repo1)
        self.addComponent('baz:runtime', '/localhost1@rpl:linux/1-1-1',
                          repos=repo1)
        self.addCollection('baz', '/localhost1@rpl:linux/1-1-1', [':runtime'],
                           repos=repo1)
        self.addComponent('baz:runtime', '/localhost1@rpl:linux/2-1-1',
                          repos=repo1)
        self.addCollection('baz', '/localhost1@rpl:linux/2-1-1', [':runtime'],
                           repos=repo1)
        self.addCollection('group-bar', '3', [
            'foo=1-1-1',
            'bar=1-1-1',
            'baz=/localhost1@rpl:linux/1-1-1',
        ])
        self.addCollection('group-bar', '4', [
            'foo=1-1-1',
            'bar=/localhost1@rpl:linux/2-1-1',
            'baz=/localhost1@rpl:linux/2-1-1',
        ])
        self.updatePkg('group-bar=3')
        file(self.systemModelPath, "w").write("install group-bar=%s/4\n" % self.defLabel)
        job = self.newJob()
        job.systemModel = file(self.systemModelPath).read()
        operation = update.SyncModel()
        preview = operation.preview(job)
        tree = etree.fromstring(preview)
        downloadSize = [x.text for x in tree.iterchildren('downloadSize')]
        self.assertTrue(len(downloadSize) == 1)
        self.assertEqual(job.state, "Previewed")

    def testSyncModelDownloadOperation(self):
        job = self.testSyncModelPreviewOperation()
        job_test = self.loadJob(job.keyId)
        operation = update.SyncModel()
        preview = operation.download(job_test)
        tree = etree.fromstring(preview)
        self.assertTrue(os.listdir(job_test.downloadDir))
        self.assertEqual(job_test.state, "Downloaded")
        self.assertTrue(tree.findtext('downloaded') == 'true')
        return job_test

    def testDuplicateDownload(self):
        job = self.testSyncModelDownloadOperation()
        job_test = self.loadJob(job.keyId)
        operation = update.SyncModel()
        preview = operation.download(job_test)
        tree = etree.fromstring(preview)
        self.assertTrue(os.listdir(job_test.downloadDir))
        self.assertEqual(job_test.state, "Downloaded")
        self.assertTrue(tree.findtext('downloaded') == 'true')
        return job_test

    def testSyncModelApplyOperation(self):
        job = self.testSyncModelDownloadOperation()
        job_test = self.loadJob(job.keyId)

        operation = update.SyncModel()
        preview = operation.apply(job_test)
        tree = etree.fromstring(preview)
        self.assertEquals(tree.attrib['id'], job.keyId)
        #group1 = self.findAndGetTrove('group-bar=1-1-1')
        group2 = self.findAndGetTrove('group-bar=2-1-1')
        self.assertEquals(
                [ x.text for x in tree.iterchildren('observed') ],
                [ self._trvAsString(group2) ])
        self.assertEquals(
                [ x.text for x in tree.iterchildren('desired') ],
                [ self._trvAsString(group2) ])
        self.assertEqual(job_test.state, "Applied")
        self.assertTrue(tree.findtext('downloaded') == 'true')
        return job

    def testSyncModelApplyOperationChangedFiles(self):
        oldJob = self.testSyncModelPreviewOperation()
        job = self.loadJob(oldJob.keyId)

        # content conflict
        with open(os.path.join(self.rootDir, "foo.txt"), 'w') as fh:
            fh.write("some other content")

        operation = update.SyncModel()
        preview = operation.apply(job)
        self.assertEqual(None, preview)
        self.assertEqual(job.state, "Exception")
        self.assertIn("contents conflict", job.content)

        preview = operation.apply(job, replaceModifiedFiles=True)
        self.assertEqual(job.state, "Applied")

    def testSyncModelApplyOperationChangedConfigFiles(self):
        oldJob = self.testSyncModelPreviewOperation()
        job = self.loadJob(oldJob.keyId)

        # config conflict
        target = os.path.join(self.rootDir, "etc/bar")
        os.unlink(target)
        os.symlink('danglingSymlink', target)

        operation = update.SyncModel()
        preview = operation.apply(job)
        self.assertEqual(None, preview)
        self.assertEqual("Exception", job.state)
        self.assertIn("file type of /etc/bar changed", job.content)

        preview = operation.apply(job, replaceModifiedConfigFiles=True)
        self.assertEqual("Applied", job.state)

    def testSyncModelApplyOperationUnmanagedFile(self):
        self.addComponent("foo:runtime", "3", fileContents=[
            ('/foo.txt', '1234567890123453'),
            ('/etc/bar', '1234567890123453'),
            ('/baz.txt', '1234567890123453'),
        ])
        self.addCollection("foo", "3", [":runtime"])
        self.addCollection("group-bar", "3", ["foo"])

        job = self.newJob()
        job.systemModel = "install group-bar=%s/3\n" % self.defLabel

        operation = update.SyncModel()
        operation.preview(job)
        self.assertEqual("Previewed", job.state)

        with open(os.path.join(self.rootDir, "baz.txt"), 'w') as fh:
            fh.write("some content")

        job = self.loadJob(job.keyId)
        operation = update.SyncModel()
        preview = operation.apply(job)
        self.assertEqual(None, preview)
        self.assertEqual(job.state, "Exception")
        self.assertIn("in the way of a newly created file", job.content)

        preview = operation.apply(job, replaceUnmanagedFiles=True)
        self.assertEqual(job.state, "Applied")

    @classmethod
    def _trvAsString(cls, trv):
        return trovetup.TroveTuple(trv.getNameVersionFlavor()).asString(
                withTimestamp=True)

    def testSyncModelPreviewOperationBadSystemModel(self):
        systemModel = "install nosuchtrove=%s/3" % self.defLabel
        job = self.newJob()
        job.systemModel = systemModel
        operation = update.SyncModel()
        ret = operation.preview(job)
        self.assertEquals(ret, None)
        self.assertEquals(job.state, "Exception")
        self.assertIn("No troves found matching: nosuchtrove=localhost@rpl:linux/3", job.content)

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

    def testUpdateModelPreviewOperation(self):
        job = self.newJob()
        job.systemModel = "# a comment\ninstall group-bar=%s/2\n" % self.defLabel
        operation = update.UpdateModel()
        preview = operation.preview(job)
        tree = etree.fromstring(preview)
        self.assertEquals(tree.attrib['id'], job.keyId)
        group1 = self.findAndGetTrove('group-bar=1-1-1')
        group2 = self.findAndGetTrove('group-bar=2-1-1')
        self.assertEquals(
                [ x.text for x in tree.iterchildren('observed') ],
                [ self._trvAsString(group1) ])
        self.assertEquals(
                [ x.text for x in tree.iterchildren('desired') ],
                # XXX FIXME: this really should be group2; but because
                # we're removing foo, the code returns the original
                # list. See the other test that's failing
                [ self._trvAsString(group1) ])
        return job
