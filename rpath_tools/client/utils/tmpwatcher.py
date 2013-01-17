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


import errno
import os
import time


class TmpWatcher(object):
    def __init__(self, dir, mtime=None, atime=None, ctime=None, prefix=None):
        self.dir = dir
        self.mtime = mtime
        self.atime = atime
        self.ctime = ctime
        self.prefix = prefix

    def _getFiles(self):
        try:
            files = [os.path.join(self.dir, x) for x in os.listdir(self.dir )]
        except OSError, err:
            if err.errno == errno.ENOENT:
                return []
            raise
        if self.prefix:
            files = [x for x in files
                    if os.path.basename(x).startswith(self.prefix) ]
        return files

    def _testFileTime(self, filepath):
        now = time.time() 
        flag = False
        if self.mtime:
            if os.stat(filepath).st_mtime < now - self.mtime * 86400:
                flag = True
        if self.ctime:
            if os.stat(filepath).st_ctime < now - self.ctime * 86400:
                flag = True
        if self.atime:
            if os.stat(filepath).st_atime < now - self.atime * 86400:
                flag = True
        return flag

    def _removeFile(self, filepath):
        try:
            if os.path.isfile(filepath):
                print "Removing %s" % filepath
                os.remove(filepath)
                return True
        except IOError, e:
            raise IOError, e

    def clean(self, delete=False):
        files = self._getFiles()
        removed = []
        for f in files:
            if os.path.isfile(f):
                if self._testFileTime(f):
                    if delete:
                        self._removeFile(f)
                    removed.append(f)
        return removed

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    survey_dir = '/var/lib/conary-cim/surveys'
    prefix = 'survey-'
    mtime = 3
    delete = False
    twatch = TmpWatcher(survey_dir, mtime=mtime, prefix=prefix)
    removed = twatch.clean(delete=delete)
    print removed
