#!/usr/bin/python
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


from rpath_tools.lib import storage_objects
from rpath_tools.lib.errors import NoUpdatesFound

import logging

logger = logging.getLogger(name = '__name__')


class UpdateSet(object):
    storagePath = "/var/lib/conary-cim/storage"

    factory = stored_objects.UpdateSetFactory

    def __init__(self):
        self.updateSet = None

    def new(self):
        self.updateSet = self.factory(self.storagePath).new()
        return self

    @classmethod
    def latestFilter(cls, obj):
        return obj.state != "Applying"

    def latest(self):
        # Make sure we filter out objects already picked up by another
        # installation service
        latest = self.factory(self.storagePath).latest(
            filter = self.latestFilter)
        if latest is None:
            raise NoUpdatesFound
        return latest

    def load(self, key):
        update = self.factory(self.storagePath).load(key)
        if update is None:
            raise NoUpdatesFound
        return update

    def _getKeyId(self):
        return self.updateSet.keyId

    keyId = property(_getKeyId)

    def _getUpdateJobDir(self):
        return self.updateSet.updateJobDir

    updateJobDir = property(_getUpdateJobDir)

