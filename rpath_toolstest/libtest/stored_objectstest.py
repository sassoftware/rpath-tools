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

from .. import testbase

from rpath_tools.lib import stored_objects

class StorageTest(testbase.TestCase):
    def testUpdateSetFactory(self):
        storagePath = self.workDir + '/storage'
        uf = stored_objects.UpdateSetFactory(storagePath)
        updateSet = uf.new()
        updateSet.content = "Installing"
        key = updateSet.keyId
        fPath = os.path.join(self.workDir, "storage",
            updateSet.prefix, key, "content")

        self.failUnlessEqual(updateSet.expiration, updateSet.updated + 36000)

        self.failUnless(os.path.exists(fPath), fPath)
        updateSet = uf.load(key)
        self.failUnlessEqual(updateSet.content, "Installing")

        self.failUnlessEqual([ x.keyId for x in uf ], [ key ])

    def testConcreteJobFactory(self):
        storagePath = self.workDir + '/storage'
        uf = stored_objects.ConcreteUpdateJobFactory(storagePath)
        concreteJob = uf.new()
        concreteJob.content = "Installing"
        self.failUnlessEqual(concreteJob.pid, None)
        concreteJob.pid = 12345
        key = concreteJob.keyId
        fPath = os.path.join(self.workDir, "storage",
            concreteJob.prefix, key, "content")
        self.failUnless(os.path.exists(fPath), fPath)
        logs = [ concreteJob.logs.add(str(x)) for x in range(3) ]

        self.failUnlessEqual(concreteJob.expiration, concreteJob.updated + 36000)

        concreteJob = uf.load(key)
        self.failUnlessEqual(concreteJob.content, "Installing")
        self.failUnlessEqual(concreteJob.pid, 12345)
        self.failUnlessEqual(list(concreteJob.logs.enumerate()), logs)

    def testExpiredKey(self):
        storagePath = self.workDir + '/storage'
        uf = stored_objects.ConcreteUpdateJobFactory(storagePath)
        concreteJob = uf.new()
        concreteJob.content = "content1"
        key1 = concreteJob.keyId

        concreteJob = uf.new()
        concreteJob.content = "content2"
        concreteJob.expiration = time.time() - 36005
        key2 = concreteJob.keyId

        keys = set(x.keyId for x in uf)
        self.failUnless(key1 in keys, "%s not in %s" % (key1, keys))
        self.failIf(key2 in keys)

    def testLatest(self):
        storagePath = self.workDir + '/storage'
        uf = stored_objects.ConcreteUpdateJobFactory(storagePath)
        concreteJob = uf.new()
        concreteJob.content = "content1"
        # Force an updated time in the past, we may be too fast and have both
        # of the keys generated the same 100th of a second.
        concreteJob.updated = concreteJob.updated - 1
        key1 = concreteJob.keyId

        concreteJob = uf.new()
        concreteJob.content = "content2"
        # Set a state, just to verify filters
        concreteJob.state = "Bloobering"
        key2 = concreteJob.keyId

        self.failUnlessEqual(uf.latest().keyId, key2)

        self.failUnlessEqual(
            uf.latest(filter = lambda x: x.state != "Bloobering").keyId,
            key1)

    def testLatestEmpty(self):
        storagePath = self.workDir + '/storage'
        uf = stored_objects.ConcreteUpdateJobFactory(storagePath)

        self.failUnlessEqual(uf.latest(), None)

    def testGetDownloadDir(self):
        storagePath = self.workDir + '/storage'
        uf = stored_objects.UpdateSetFactory(storagePath)

        uset = uf.new()
        dname = uset.downloadDir
        self.failUnless(os.path.isdir(dname))
        self.failUnless(dname.endswith('downloaded-changesets'))

        dname = uset.updateJobDir
        self.failUnless(os.path.isdir(dname))
        self.failUnless(dname.endswith('update-job'))

class SimpleStorageTests(testbase.TestCase):
    def testSimpleStorage(self):
        storagePath = self.workDir + '/storage'

        class TestObject(stored_objects.FlatStoredObject):
            prefix = "test"

        sf = stored_objects.StoredObjectsFactory(storagePath)
        sf.factory = TestObject

        o1 = sf.new()
        o1.content = "o1"

        o2 = sf.new()
        o2.content = "o2"

        expected = sorted([o1, o2], key = lambda x: x.keyId)

        objs = list(sf)
        self.failUnlessEqual(
            [ x.keyId for x in expected ],
            [ x.keyId for x in objs ])
        self.failUnlessEqual(
            [ x.content for x in expected ],
            [ x.content for x in objs ])
        self.failUnlessEqual(
            [ x.created for x in expected ],
            [ x.created for x in objs ])
        self.failUnlessEqual(
            [ x.updated for x in expected ],
            [ x.updated for x in objs ])

        for obj in expected:
            nobj = sf.load(obj.keyId)
            self.failUnlessEqual(nobj.keyId, obj.keyId)
