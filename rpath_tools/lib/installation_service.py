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

import os

from conary.cmds import updatecmd
from conary.deps import deps
from conary import conaryclient
from conary import versions
from conary import trovetup

from rpath_tools.lib import formatter, stored_objects, update

import sys
# log.syslog.command() attempts to use sys.argv
if not hasattr(sys, 'argv'):
    sys.argv = []

class InstallationServiceError(Exception):
    "Base class"

class NoUpdatesFound(InstallationServiceError):
    "Raised when no updates are available"

class RepositoryError(InstallationServiceError):
    "Raised when a repository error is caught"

class UpdateFlags(object):
    __slots__ = [ 'migrate', 'update', 'updateall', 'sync', 'test' ]
    def __init__(self, **kwargs):
        for s in self.__slots__:
            setattr(self, s, kwargs.pop(s, None))

class UpdateSet(object):
    storagePath = "/var/lib/conary-cim/storage"

    factory = stored_objects.ConcreteUpdateJobFactory

    def __init__(self):
        self.updateSet = None

    def new(self):
        self.updateSet = self.factory(self.storagePath).new()
        return self

    @classmethod
    def latestFilter(cls, obj):
        ujDir = obj.updateJobDir
        return os.path.exists(os.path.join(ujDir, 'jobfile')) and obj.state != "Applying"

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

    def _getUpdateJobDir(self):
        return self.updateSet.updateJobDir

    updateJobDir = property(_getUpdateJobDir)

class InstallationService(update.UpdateService):
    UpdateSetFactory = UpdateSet
    UpdateFlags = UpdateFlags
    # XXX we should find a better place for these
    SystemModelID = 'com.rpath.conary:system_model'
    SystemModelElementName = 'system model'
    SystemModelType = object()

    def buildUpdateJob(self, applyList):
        # We need to update to the latest version, so drop the version
        # information from applyList
        applyList = [ (x[0], x[1], (None, None), True) for x in applyList ]
        flags = UpdateFlags(update = True)
        return self._newUpdateJob(applyList, flags)

    def _newUpdateJob(self, applyList, flags):
        cclient = self.conaryClient
        updateJob = cclient.newUpdateJob()
        try:
            #suggMap = cclient.prepareUpdateJob(updateJob, applyList,
            #   migrate = flags.migrate, test = flags.test)
            # TODO if systemmodel...
            suggMap = cclient.prepareUpdateJob(updateJob, applyList,
                migrate = flags.migrate, sync = flags.sync, test = flags.test)
        except conaryclient.NoNewTrovesError:
            raise NoUpdatesFound
        except conaryclient.errors.RepositoryError, e:
            raise RepositoryError, e, sys.exc_info()[2]
        return updateJob

    def freezeUpdateJob(self, updateJob):
        us = self.UpdateSetFactory().new()
        freezeDir = us.updateJobDir
        updateJob.freeze(freezeDir)
        return us

    def thawUpdateJob(self, instanceId=None):
        if instanceId:
            keyId = instanceId.split(':')[1]
            job = self.UpdateSetFactory().load(keyId)
        else:
            job = self.UpdateSetFactory().latest()
            keyId = job.keyId

        cclient = self.conaryClient
        updateJob = cclient.newUpdateJob()
        updateJob.thaw(job.updateJobDir)
        return keyId, updateJob, job

    def updateAllCheck(self):
        applyList = self.getUpdateItemList()
        try:
            updateJob = self.buildUpdateJob(applyList)
        except NoUpdatesFound:
            return
        except RepositoryError, e:
            # XXX FIXME: store the exception somewhere
            raise

        self.freezeUpdateJob(updateJob)

    def getUpdateItemList(self):
        cclient = self.conaryClient

        updateItems = cclient.getUpdateItemList()
        applyList = [ (x[0], (None, None), x[1:], True) for x in updateItems ]
        return applyList

    def getAvailableUpdatesList(self):
        "Return the list of available updates from a frozen update job"
        try:
            jobId, updateJob, concreteJob = self.thawUpdateJob()
        except NoUpdatesFound:
            return None, []
        return jobId, updateJob.primaries

    def updateAllApply(self, instanceId):
        try:
            jobId, updateJob, updateSet = self.thawUpdateJob(instanceId)
        except NoUpdatesFound:
            return None
        # Set the state, so we don't pick this update set object again
        updateSet.state = "Applying"

        self.fixSignals()
        self.conaryClient.applyUpdateJob(updateJob)

    def getCurrentTop(self):
        """Return the tuple for the present top-level group"""
        topLevelItems = sorted(self.conaryClient.getUpdateItemList())
        for name, version, flavor in topLevelItems:
            if name.startswith('group-') and name.endswith('-appliance'):
                break
        else:
            print 'Unable to find top-level group'
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

    @classmethod
    def parseTroveSpec(cls, troveSpec):
        n, v, f = conaryclient.cmdline.parseTroveSpec(troveSpec)
        if f is None:
            f = deps.parseFlavor('')
        v = versions.VersionFromString(v)
        return (n, v, f)

    def updateOperation(self, job, sources, flags):
        trvSpecList = [ self.parseTroveSpec(x) for x in sources ]
        jobList = [ (x[0], (None, None), (x[1], x[2]), True)
            for x in trvSpecList ]
        cclient = self.conaryClient
        oldTop = self.getCurrentTop()
        callback = UpdateCallback(job)
        cclient.setUpdateCallback(callback)
        try:
            updateJob = self._newUpdateJob(jobList, flags)
            newTop = self.getUpdatedTop(oldTop, updateJob)
        except NoUpdatesFound:
            updateJob = None
            newTop = oldTop
        fmt = formatter.Formatter(updateJob)
        fmt.format()
        fmt.addDesiredVersion(newTop)
        if flags.test or updateJob is None:
            fmt.addObservedVersion(oldTop)
            return fmt.toxml()
        self.fixSignals()
        cclient.applyUpdateJob(updateJob, test=bool(flags.test))
        actualTop = self.getCurrentTop()
        fmt.addObservedVersion(actualTop)
        return fmt.toxml()

    def createTroveMapping(self):
        """
        @return: a dictionary keyed on the full trove spec, with a tuple
            ((name, version, flavor), isInstalled) as value
        """
        troveList = self.getUpdateItemList()
        # True for installed troves, False for available troves
        troveMapping = dict(
            ("rpath.com:%s=%s[%s]" % (n, v.freeze(), f), ((n, v, f), True))
                for (n, (_, _), (v, f), _) in troveList)
        jobId, troveList = self.getAvailableUpdatesList()
        if jobId is not None:
            troveMapping.update(dict(
                ("rpath.com:%s:%s" % (jobId, i), ((n, v, f), False))
                    for i, (n, (_, _), (v, f), _) in enumerate(troveList)))
        systemModel = self.conaryClient.getSystemModel()
        if systemModel:
            contents = systemModel.contents
            mtime = int(systemModel.mtime)
            value = ('system model', contents, mtime)
            troveMapping[self.SystemModelID] = (value, self.SystemModelType)
        return troveMapping


class UpdateCallback(updatecmd.UpdateCallback):
    class LogStream(object):
        def __init__(self, job):
            self.job = job
        def write(self, text):
            self.job.logs.add(text)

    def __init__(self, job):
        updatecmd.UpdateCallback.__init__(self)
        self.job = job
        self.out = self.LogStream(job)

    def _message(self, text):
        if not text:
            return
        self.job.logs.add(text)

    def done(self):
        self.job.logs.add("Done")
    updateDone = done
