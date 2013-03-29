#!/usr/bin/python2.4
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

import storage

class Log(object):
    __slots__ = [ 'timestamp', 'content' ]
    def __init__(self, **kwargs):
        for s in self.__slots__:
            setattr(self, s, kwargs.pop(s))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self.timestamp == other.timestamp and
                self.content == other.content)

    def __repr__(self):
        return "<%s object at %s; timestamp=%s>" % (self.__class__.__name__,
            id(self), self.timestamp)

    __str__ = __repr__

class LogEntryMixIn(object):
    class _LogList(object):
        _subdir = 'logs'
        def __init__(self, keyId, storage):
            self.keyId = keyId
            self.storage = storage

        def add(self, content, timestamp = None):
            if timestamp is None:
                timestamp = time.time()
            if isinstance(timestamp, basestring):
                timestamp = float(timestamp)
            for i in range(10):
                # Catch collisions. This is not intended to be cross-process
                # foolproof
                key = (self.keyId, self._subdir, "%.4f" % timestamp)
                if not self.storage.exists(key):
                    break
                timestamp += 0.0001
            self.storage.set(key, content)
            return Log(timestamp = key[-1], content = content)

        def enumerate(self):
            for key in sorted(self.storage.enumerate((self.keyId, self._subdir))):
                fname = self.storage.getFileFromKey(key)
                yield Log(timestamp = os.path.basename(fname),
                    content = file(fname).read())

    @property
    def logs(self):
        return self._LogList(self.keyId, self.storage)

class StateMixIn(object):
    def _setState(self, state):
        assert self.keyId is not None
        self._setUpdated()
        return self.storage.set((self.keyId, 'state'), state)

    def _getState(self):
        assert self.keyId is not None
        return self.storage.get((self.keyId, 'state'))

    def _deleteState(self):
        assert self.keyId is not None
        self._setUpdated()
        return self.storage.delete((self.keyId, 'state'))

    state = property(_getState, _setState, _deleteState)

class BaseStoredObject(object):
    prefix = None
    ttl = 3600 * 10 # Expiration, in seconds
    keyPrefix = None

    def __init__(self, storagePath, keyId = None):
        self.storage = self.getStorage(storagePath)
        if keyId is None:
            self.keyId = None
        else:
            self.keyId = self.storage._sanitizeKey(keyId)

    @classmethod
    def getStorage(cls, storagePath):
        return storage.DiskStorage(storage.StorageConfig(
            os.path.join(storagePath, cls.prefix)))

    def new(self):
        self.keyId = self.storage.newKey(keyPrefix=self.keyPrefix)
        self._setCreated()
        return self.keyId

    def _setCreated(self, tstamp = None):
        assert self.keyId is not None
        tstamp = self._setUpdated(tstamp)
        self.storage.set((self.keyId, 'created'), tstamp)
        return tstamp

    def _getCreated(self):
        return self._getTimestamp('created')

    created = property(_getCreated, _setCreated)

    def _setContent(self, content):
        assert self.keyId is not None
        self._setUpdated()
        if content is None:
            self.storage.delete((self.keyId, 'content'))
            return None
        return self.storage.set((self.keyId, 'content'), content)

    def _getContent(self):
        assert self.keyId is not None
        return self.storage.get((self.keyId, 'content'))

    content = property(_getContent, _setContent)

    def _getUpdated(self):
        return self._getTimestamp('updated')

    def _setUpdated(self, tstamp = None):
        assert self.keyId is not None
        if tstamp is None:
            tstamp = time.time()
        expiration = tstamp + self.ttl
        tstamp = "%.2f" % tstamp
        self.storage.set((self.keyId, 'updated'), tstamp)
        self._setExpiration(expiration)
        return tstamp

    updated = property(_getUpdated, _setUpdated)

    def _setExpiration(self, tstamp):
        tstamp = "%.2f" % tstamp
        self.storage.set((self.keyId, 'expiration'), tstamp)
        return tstamp

    def _getExpiration(self):
        return self._getTimestamp('expiration')

    expiration = property(_getExpiration, _setExpiration)

    def _getTimestamp(self, kfile):
        assert self.keyId is not None
        tstamp = self.storage.get((self.keyId, kfile))
        if tstamp is not None:
            tstamp = tstamp.strip()
            if tstamp:
                return float(tstamp)
        return None

class StoredObject(BaseStoredObject, LogEntryMixIn, StateMixIn):
    pass

class ConcreteUpdateJob(StoredObject):
    prefix = "jobs"
    keyPrefix = "updates"

    def _setPid(self, pid):
        assert self.keyId is not None
        return self.storage.set((self.keyId, "pid"), pid)

    def _getPid(self):
        assert self.keyId is not None
        pid = self.storage.get((self.keyId, 'pid'))
        if pid is None:
            return None
        return int(pid.strip())

    pid = property(_getPid, _setPid)

    @property
    def frozenUpdateJobDir(self):
        downloadDir = self.storage.newCollection((self.keyId, "frozen-update-job"))
        return self.storage.getFileFromKey(downloadDir)

    def _getSystemModel(self):
        return self.storage.get((self.keyId, "systemModel"))

    def _setSystemModel(self, systemModel):
        return self.storage.set((self.keyId, "systemModel"), systemModel)

    systemModel = property(_getSystemModel, _setSystemModel)

class ConcreteSurveyJob(ConcreteUpdateJob):
    keyPrefix = "surveys"

class UpdateSet(StoredObject):
    prefix = "updates"

    def _getDownloadDir(self):
        downloadDir = self.storage.newCollection((self.keyId, "downloaded-changesets"))
        return self.storage.getFileFromKey(downloadDir)

    downloadDir = property(_getDownloadDir)

    def _getUpdateJobDir(self):
        ujDir = self.storage.newCollection((self.keyId, "update-job"))
        return self.storage.getFileFromKey(ujDir)

    updateJobDir = property(_getUpdateJobDir)

class StoredObjectsFactory(object):
    factory = None
    def __init__(self, storagePath):
        self.storagePath = storagePath

    def load(self, key):
        obj = self.factory(self.storagePath, keyId = key)
        return obj

    def new(self):
        obj = self.factory(self.storagePath)
        obj.new()
        return obj

    def latest(self, filter = None):
        """
        Return the object that was modified the latest, or None if no object
        is found
        """
        retobj = None
        maxModified = None
        for obj in self:
            updated = obj.updated
            if maxModified is None or updated > maxModified:
                if filter is not None and not filter(obj):
                    continue
                maxModified = updated
                retobj = obj
        return retobj

    def __iter__(self):
        strg = self.factory.getStorage(self.storagePath)
        now = time.time()
        for key in strg.enumerate(keyPrefix=self.factory.keyPrefix):
            obj = self.factory(self.storagePath, keyId = key)
            expiration = obj.expiration
            if expiration and expiration < now:
                strg.delete(key)
                continue
            yield obj

class ConcreteUpdateJobFactory(StoredObjectsFactory):
    factory = ConcreteUpdateJob

class ConcreteSurveyJobFactory(StoredObjectsFactory):
    factory = ConcreteSurveyJob

class UpdateSetFactory(StoredObjectsFactory):
    factory = UpdateSet

class FlatStoredObject(BaseStoredObject):
    def _setContent(self, content):
        assert self.keyId is not None
        self._setUpdated()
        return self.storage.set(self.keyId, content)

    def _getContent(self):
        assert self.keyId is not None
        return self.storage.get(self.keyId)

    content = property(_getContent, _setContent)

    def _getCreated(self):
        return self._getUpdated()

    def _setCreated(self, tstamp = None):
        assert self.keyId is not None
        self._setContent('')
        tstamp = self._setUpdated(tstamp)
        return tstamp

    # We specifically don't allow to set the created time
    created = property(_getCreated)

    def _getUpdated(self):
        assert self.keyId is not None
        fname = self.storage._getFileForKey(self.keyId)
        try:
            return os.stat(fname).st_mtime
        except OSError, e:
            if e.errno != 2:
                raise
            return None

    def _setUpdated(self, tstamp = None):
        assert self.keyId is not None
        if tstamp is None:
            tstamp = time.time()
        fname = self.storage._getFileForKey(self.keyId)
        try:
            os.utime(fname, (tstamp, tstamp))
        except OSError, e:
            if e.errno != 2:
                raise
            return None
        return tstamp

    updated = property(_getUpdated, _setUpdated)

    def _setExpiration(self, tstamp):
        return tstamp

    def _getExpiration(self):
        return self._getUpdated() + self.ttl

    expiration = property(_getExpiration, _setExpiration)
