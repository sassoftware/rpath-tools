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
        if self.prefix:
            files = [ os.path.join(self.dir, x) for x in os.listdir(self.dir ) 
                        if x.startswith(self.prefix)]
            return files
        files = [ os.path.join(self.dir, x) for x in os.listdir(self.dir) ]
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
                os.remove(filepath)
                return True
        except IOError, e:
            raise IOError

    def clean(self):
        files = self._getFiles()
        removed = []
        for f in files:
            if os.path.isfile(f):
                if self._testFileTime(f):
                    #self._removeFile(f)
                    removed.append(f)
        return removed

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    survey_dir = '/var/lib/conary-cim/surveys'
    prefix = 'survey-'
    mtime = 3
    twatch = TmpWatcher(survey_dir, mtime=mtime, prefix=prefix)
    removed = twatch.clean()
    print removed
