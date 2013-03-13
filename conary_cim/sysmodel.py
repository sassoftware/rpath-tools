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


from conary.conaryclient import systemmodel

import time


import logging

logger = logging.getLogger(name = '__name__')


class SystemModel(systemmodel.SystemModelFile):
    def __init__(self, sysmodel):
        super(SystemModel, self).__init__(
            sysmodel.model, sysmodel.fileName)
        self._lkg = sysmodel.fileName
        self._version = None
        self._restore = False
        self._sysmodel = sysmodel
        # FIXME Not sure why I bothered to extend

    def rollback(self, version):
        '''
        rollback to LKG eor a specific version
        '''
        pass

    def version(self):
        '''
        save current sysmodel to versioned file or lkg
        '''
        if not self._version:
            self._version = str(time.time())
        versioned = '.'.join([self.fileName, self._version])
        try:
            self.write(fileName=versioned)
        except:
            raise Exception
        snapshot = self.read(fileName=versioned)
        return snapshot

    def save(self, fileName):
        '''
        pass a sysmodel to get written to disk
        '''
        try:
            self.write(fileName=fileName)
        except:
            return None
        snapshot = self.read(fileName=fileName)
        return snapshot

    def snapshot(self, fileName):
        '''
        pass a sysmodel to get written to disk
        '''
        try:
            self.writeSnapshot(fileName=fileName)
            self.snapName = fileName
        except:
            return None
        snapshot = self.read(fileName=self.snapName)
        return snapshot

    def commit(self):
        '''
        clean up the system model mess after moving to the latest
        '''
        try:
            self.closeSnapshot()
        except:
            return False
        return True

    def clean(self):
        '''
        clean up the system model mess after moving to the latest
        '''
        try:
            self.deleteSnapshot()
        except:
            return False
        return True


    def restore(self, fileName):
        '''
        apply a restored sysmodeel
        '''
        try:
            self.parse(fileName=fileName)
            self.write(fileName=self.fileName)
        except:
            raise Exception
        return True

    def debug(self):
        import epdb;epdb.st()


