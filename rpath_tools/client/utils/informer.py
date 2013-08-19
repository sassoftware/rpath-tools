
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


from conary import conaryclient
from conary import trovetup
from conary.lib import util

from rpath_tools.lib import update

import os

import json


import logging

logger = logging.getLogger(__name__)

class InformerError(Exception):
    "Base class"

class NoUpdatesFound(InformerError):
    "Raised when no updates are available"

class RepositoryError(InformerError):
    "Raised when a repository error is caught"



class InformerFlags(object):
    __slots__ = [ 'top', 'updates', 'counter', 'sync',
                    'test', 'json', 'xml', 'html', 'python', ]
    def __init__(self, **kwargs):
        for s in self.__slots__:
            setattr(self, s, kwargs.pop(s, False))

    def update(self, kwds):
        for key, value in kwds.items():
            setattr(self, key, value)

    def get(self, flag):
        return getattr(self, flag)

    @property
    def items(self):
        return self.__slots__


class Informer(update.UpdateService):

    def __init__(self, values=[], callback=None):
        '''
        Base Module Class
        @param value: A list representing the information types desired
        @type value: list
        @param callback: A callback for messaging can be None
        @type callback: object like updatecmd.Callback
        '''
        super(Informer, self).__init__()
        if not self.systemModelPath:
            self.systemModelPath = self.conaryCfg.modelPath
        self.tmpDir = self.conaryCfg.tmpDir

        self._values = dict([ (x, True) for x in values])
        self.flags = InformerFlags()
        if self._values:
            self.flags.update(self._values)
        self._callback = callback
        self._client = None
        self._cfg = None

        self._functionMap = dict([('top', self.getTopLevelItems),
                                 ('updates', self.getTopLevelItemsAllVersions),
                                 ('counter', self.getTransactionCounter),
                            ])



    def _runProcess(self, cmd):
        '''cmd @ [ '/sbin/service', 'name', 'status' ]'''
        import subprocess
        try:
            proc = subprocess.Popen(    cmd,
                                        shell=False,
                                        stdin=None,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE
                                    )
            stdout, stderr = proc.communicate()
            # TODO: Fix results up if we add serious logging...
            #if proc.returncode != 0:
                #raise Exception("%s failed with return code %s" %
                #            (' '.join(cmd), proc.returncode))
                #return stderr.decode("UTF8")
            return stdout.decode("UTF8")
        except Exception, ex:
            logger.error("%s failed: %s" %
                            (' '.join(cmd), str(ex)))
            return str(ex)

    @classmethod
    def parseTroveSpec(cls, troveSpec):
        from conary import versions
        n, v, f = conaryclient.cmdline.parseTroveSpec(troveSpec)
        try:
            # Conary doesn't like being passed frozen versions, so try to parse
            # it and if it works use the object.
            v = versions.ThawVersion(v)
        except ValueError:
            pass
        return (n, v, f)



    def storeInFile(self, data, fileName):
        '''
        Writes data to the specified file
        overwrites the specified file if file exists.
        @param data: Text to be stored in file
        @type data: string
        @param filename: name of file to which to write the data
        @type filename: string
        '''
        import tempfile, stat

        if os.path.exists(fileName):
            fileMode = stat.S_IMODE(os.stat(fileName)[stat.ST_MODE])
        else:
            fileMode = 0644

        dirName = os.path.dirname(fileName)
        fd, tmpName = tempfile.mkstemp(prefix='stored', dir=dirName)
        try:
            f = os.fdopen(fd, 'w')
            f.write(str(data))
            os.chmod(tmpName, fileMode)
            os.rename(tmpName, fileName)
        except Exception, e:
            #FIXME
            return Exception, str(e)
        return True, fileName

    def readStoredFile(self, fileName):
        '''
        Read a stored file and return its contents in a string
        @param fileName: Name of the file to read
        @type fileName: string
        '''
        blob = ""
        try:
            with open(fileName) as f:
                blob = f.read()
        except EnvironmentError, e:
            #FIXME
            return str(e)
        return blob

    def readStoredFileList(self, fileName):
        '''
        Read a stored file and return its contents in a list
        @param fileName: Name of the file to read
        @type fileName: string
        '''
        data = []
        try:
            with open(fileName) as f:
                data = f.readlines()
        except EnvironmentError, e:
            #FIXME
            return [ EnvironmentError, str(e) ]
        return data

    def _sanitize(self, trovelist):
        sanitized = []
        for name, version, flavors in trovelist:
            try:
                version = str(version)
            except:
                pass
            try:
                flavors = [ str(x) for x in flavors ]
            except:
                pass
            sanitized.append((name, version, flavors))
        return sanitized

    def _jsonify(self, data):
        '''
        Do some json stuff
        '''
        return json.dumps(data)

    def mangle(self, data):
        mangled = data
        if self.flags.json:
            mangled = self._jsonify(data)
        if self.flags.xml:
            mangled = self._xmlify(data)
        if self.flags.html:
            mangled = self._htmlify(data)
        if self.flags.python:
            mangled = self._pythonify(data)
        return mangled

    def _getTopLevelItemsAllVersions(self):
        topLevelItems = self._getTopLevelItems()
        allversions = {}
        tops = [ trovetup.TroveTuple(name, version, flavor)
                for name, version, flavor in topLevelItems ]
                    #if name.startswith('group-') ][0]
        for top in tops:
            label = top.version.trailingLabel()
            query = { top.name : { label : None } }
            allversions.update(self.conaryClient.repos.getTroveVersionsByLabel(query))
        return allversions

    def _getTopLevelItems(self):
        return sorted(self.conaryClient.getUpdateItemList())

    def _getTransactionCounter(self):
        db = self.conaryClient.getDatabase()
        return db.getTransactionCounter()

    def getTransactionCounter(self):
        tcounter = self._getTransactionCounter()
        tcount = {}
        tcount.setdefault('conaryDbTransactionCounter',
                                ['Count', str(tcounter)])
        return self.mangle(tcount)


    def getTopLevelItemsAllVersions(self):
        all = self._getTopLevelItemsAllVersions()
        allversions = {}
        for name, versions in all.items():
            trovelist = []
            for version, flavors in versions.items():
                if self.conaryCfg.flavorPreferences:
                    flavor = [ flavor for flavor in flavors if flavor.satisfies(self.conaryCfg.flavorPreferences[0]) ]
                if flavor:
                    trovelist.append([ name, version, flavor ]) 
            allversions.setdefault(name, self._sanitize(sorted(trovelist)))
        return self.mangle(allversions)

    def getTopLevelItems(self):
        topLevelItems = {}
        items = self._getTopLevelItems()
        topLevelItems.setdefault('topLevelItems', self._sanitize(items))
        return self.mangle(topLevelItems)

    def _runFunction(self, function):
        return self._functionMap[function]()

    def inform(self):
        results = ''
        for item in self.flags.items:
            if self.flags.get(item) and item in self._functionMap:
                results = "%s\n%s" % (results, self._runFunction(item))
        return results


    def debug(self):
        top = self.getTopLevelItems()
        tcount = self.getTransactionCounter()
        alltop = self.getTopLevelItemsAllVersions()
        return top, tcount, alltop


if __name__ == '__main__':
    import sys
    sys.excepthook = util.genExcepthook()

    items = [ 'top', 'updates', 'counter', 'sync',
                    'test', 'json' ]

    obj = Informer(items)
    obj.debug()

