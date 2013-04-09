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
from conary import versions

from rpath_tools.lib import formatter
from rpath_tools.lib import clientfactory
from rpath_tools.lib import concrete_job

import os
import logging

logger = logging.getLogger(name='__name__')

class InstallationServiceError(Exception):
    "Base class"

class NoUpdatesFound(InstallationServiceError):
    "Raised when no updates are available"

class RepositoryError(InstallationServiceError):
    "Raised when a repository error is caught"

class UpdateFlags(object):
    __slots__ = [ 'migrate', 'update', 'updateall', 'test' ]
    def __init__(self, **kwargs):
        for s in self.__slots__:
            setattr(self, s, kwargs.pop(s, None))




class Preview(object):
    conaryClientFactory = clientfactory.ConaryClientFactory

    def __init__(self, cclient=None):
        self.cclient = cclient

    def _getClient(self, force=False):
        if self.cclient is None or force:
            self.cclient = self.conaryClientFactory().getClient()
        return self.cclient

    conaryClient = property(_getClient)

    @classmethod
    def parseTroveSpec(cls, troveSpec):
        n, v, f = conaryclient.cmdline.parseTroveSpec(troveSpec)
        try:
            # Conary doesn't like being passed frozen versions, so try to parse
            # it and if it works use the object.
            v = versions.ThawVersion(v)
        except ValueError:
            pass
        return (n, v, f)

    def _system_model_exists(self):
        cfg = self.conaryClientFactory().getCfg()
        return os.path.isfile(cfg.modelPath)

    is_system_model = property(_system_model_exists)

    def _newUpdateJob(self, applyList, flags):
        cclient = self.conaryClient
        updateJob = cclient.newUpdateJob()
        try:
            suggMap = cclient.prepareUpdateJob(updateJob, applyList,
                migrate = flags.migrate, test = flags.test)
        except conaryclient.NoNewTrovesError:
            raise NoUpdatesFound
        except conaryclient.errors.RepositoryError, e:
            raise RepositoryError, e
        return updateJob

    def _fixSignals(self):
        # TODO: Fix this hack.
        # sfcb broker overrides these signals, but the python library thinks
        # the handlers are None.  This breaks the sigprotect.py conary
        # library.
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        signal.signal(signal.SIGUSR1, signal.SIG_DFL)

    def getCurrentTop(self):
        """Return the tuple for the present top-level group"""
        topLevelItems = sorted(self.conaryClient.getUpdateItemList())
        for name, version, flavor in topLevelItems:
            if name.startswith('group-') and name.endswith('-appliance'):
                break
        else:
            logger.warn('Unable to find top-level group')
            return None
        return trovetup.TroveTuple(name, version, flavor)

    def getUpdatedTop(self, topTuple, updateJob):
        """
        Return the tuple for the new top-level group after applying an
        update job.
        """
        added = set()
        topErased = False
        for jobList in updateJob.getJobs():
            for (name, (oldVersion, oldFlavor), (newVersion, newFlavor),
                    isAbsolute) in jobList:
                if name == topTuple.name:
                    if newVersion:
                        return trovetup.TroveTuple(name, newVersion, newFlavor)
                    else:
                        # The top-level group is being erased, so look for
                        # another group being installed
                        topErased = True
                elif oldVersion is None and name.startswith('group-'):
                    added.add(trovetup.TroveTuple(name, newVersion, newFlavor))
        if topErased and added:
            # A common anti-pattern...
            appliances = sorted(x for x in added
                    if x.name.endswith('-appliance'))
            if appliances:
                return appliances[0]
            else:
                # Pick any group
                return sorted(added)[0]
        # Not mentioned, so reuse the old version. Migrating to "remediate" a
        # system back to its nominal group would cause this, for example.
        return topTuple

    def updateOperation(self, sources, flags, callback=None):
        '''Use updateOperation to create a preview by setting flag.test'''
        cclient = self.conaryClient
        oldTop = self.getCurrentTop()
        trvSpecList = [ self.parseTroveSpec(x) for x in sources ]
        if not trvSpecList:
            if oldTop is not None:
                # No destination was provided, so use the existing version.
                trvSpecList = [ oldTop ]
            else:
                # During assimilation we don't have anything
                return None
        jobList = [ (x[0], (None, None), (x[1], x[2]), True)
            for x in trvSpecList ]
        cclient.setUpdateCallback(callback)
        try:
            updateJob = self._newUpdateJob(jobList, flags)
            newTop = self.getUpdatedTop(oldTop, updateJob)
        except NoUpdatesFound:
            logger.warn('No Updates Found')
            updateJob = None
            newTop = oldTop
        fmt = formatter.Formatter(updateJob)
        fmt.format()
        fmt.addDesiredVersion(newTop)
        if flags.test or updateJob is None:
            fmt.addObservedVersion(oldTop)
            return fmt.toxml()
        return None

    def preview(self, sources):
        flags = UpdateFlags(migrate=True,test=True)
        if self.is_system_model:
            fname = "/tmp/system-model.preview"
            file(fname, "w").write(sources)
            concreteJob = concrete_job.UpdateJob.previewSyncOperation(fname, flags)
            xml = concreteJob.contents
        else:
            xml = self.updateOperation(sources, flags)
        if xml:
            return xml
        return '<preview/>'

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    sources = [ 'group-smitty-c6e-goad-appliance=/smitty-c6e-goad.eng.rpath.com@rpath:smitty-c6e-goad-1-devel/1-63-1' ]
    preview = Preview()
    xml = preview.preview(sources)
    print xml
