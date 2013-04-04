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

from rpath_tools.lib import installation_service

class InstallationService(installation_service.InstallationService):
    SystemModelID = 'com.rpath.conary:system_model'
    SystemModelElementName = 'system model'
    SystemModelType = object()

    def updateAllCheck(self):
        applyList = self.getUpdateItemList()
        try:
            updateJob = self.buildUpdateJob(applyList)
        except installation_service.NoUpdatesFound:
            return
        except installation_service.RepositoryError, e:
            # XXX FIXME: store the exception somewhere
            raise

        self.freezeUpdateJob(updateJob)

    def run(self):
        self.updateAllCheck()

    def getAvailableUpdatesList(self):
        "Return the list of available updates from a frozen update job"
        try:
            jobId, updateJob, concreteJob = self.thawUpdateJob()
        except installation_service.NoUpdatesFound:
            return None, []
        return jobId, updateJob.primaries

    def updateAllApply(self, instanceId):
        try:
            jobId, updateJob, updateSet = self.thawUpdateJob(instanceId)
        except installation_service.NoUpdatesFound:
            return None
        # Set the state, so we don't pick this update set object again
        updateSet.state = "Applying"

        self._fixSignals()
        self.conaryClient.applyUpdateJob(updateJob)

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
