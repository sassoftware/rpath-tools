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


from conary import conarycfg
from conary import errors as cerrors
from conary import trovetup

from conary.conaryclient import cml
from conary.conaryclient import systemmodel
from conary.conaryclient import modelupdate
from conary.repository import errors as repo_errors
from conary.lib import util


from rpath_tools.lib import errors
from rpath_tools.lib import clientfactory
from rpath_tools.lib import callbacks
from rpath_tools.lib import formatter

import copy
import itertools
import types
import time
import os
import logging
import traceback

logger = logging.getLogger(__name__)



class SystemModelFlags(object):
    __slots__ = [ 'migrate', 'update', 'updateall', 'sync', 'test',
                    'freeze', 'thaw', 'iid',  'preview', 'apply', ]
    def __init__(self, **kwargs):
        for s in self.__slots__:
            setattr(self, s, kwargs.pop(s, None))

class UpdateService(object):
    conaryClientFactory = clientfactory.ConaryClientFactory

    def __init__(self):
        self._cclient = None
        self._cfg = None

    def _getClient(self, modelfile=None, force=False):
        if self._cclient is None or force:
            if self.isSystemModel:
                self._cclient = self.conaryClientFactory().getClient(
                                            modelFile=modelfile)
            else:
                self._cclient = self.conaryClientFactory().getClient(
                                            model=False)
        return self._cclient

    conaryClient = property(_getClient)

    def _getCfg(self, force=False):
        if self._cfg is None or force:
            self._cfg = self.conaryClientFactory().getCfg()
        return self._cfg

    conaryCfg = property(_getCfg)

    @property
    def isSystemModel(self):
        return os.path.isfile(self.systemModelPath)

    @property
    def systemModelPath(self):
        cfg = self.conaryCfg
        return util.joinPaths(cfg.root, cfg.modelPath)

    @classmethod
    def fixSignals(cls):
        # sfcb broker overrides these signals, but the python library thinks
        # the handlers are None.  This breaks the sigprotect.py conary
        # library.
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        signal.signal(signal.SIGUSR1, signal.SIG_DFL)


class SystemModel(UpdateService):
    def __init__(self, sysmod=None, callback=None):
        '''
        sysmod is a system-model string that will over write the current
        system-model.
        @param sysmod: A string representing the contents of a system-model file
        @type sysmod: String
        @param callback: A callback for messaging can be None
        @type callback: object like updatecmd.Callback
        '''
        super(SystemModel, self).__init__()
        self._sysmodel = None
        self._newSystemModel = None
        self._contents = sysmod
        if self._contents:
            self._newSystemModel = self._setSystemModelContents(self._contents)
        self._manifest = None
        self._model_cache = None
        self._cfg = self.conaryClientFactory().getCfg()
        self._call = callback

    def _getSystemModelContents(self):
        return self._newSystemModel

    def _setSystemModelContents(self, contents):
        if isinstance(contents, types.StringTypes):
            contents = [ x + '\n' for x in
                                contents.split('\n') if x ]
        self._newSystemModel = contents

    system_model = property(_getSystemModelContents, _setSystemModelContents)

    def _cache(self, callback=None, changeSetList=[], loadTroveCache=True):
        '''
        Create a model cache to use for updates
        '''
        cclient = self.conaryClient
        cclient.cfg.initializeFlavors()
        cfg = cclient.cfg
        try:
            self._model_cache = modelupdate.CMLTroveCache(
                cclient.getDatabase(),
                cclient.getRepos(),
                callback = callback,
                changeSetList = changeSetList,
                )
            if loadTroveCache:
                self._model_cache_path = ''.join([cfg.root,
                                    cfg.dbPath, '/modelcache'])
                if os.path.exists(self._model_cache_path):
                    logger.info("loading model cache from %s",
                                    self._model_cache_path)
                    if callback:
                        callback.loadingModelCache()
                    self._model_cache.load(self._model_cache_path)
            return self._model_cache
        except:
            return None

    def _troves(self):
        troves = self._model_cache.getTroves(
                [ x[0] for x in self._manifest ])
        return troves

    # BASIC UTILS

    def readStoredSystemModel(self, fileName):
        '''
        Read a stored system-model file and return its contents in a list
        @param fileName: Name of the file to read
        @type fileName: string
        '''
        data = []
        try:
            with open(fileName) as f:
                data = f.readlines()
        except EnvironmentError, e:
            raise
        return data


    # SYSTEM MODEL FUNCTIONS

    def _getSystemModel(self):
        '''
        get current system model from system
        '''
        cclient = self.conaryClient
        self.sysmodel = cclient.getSystemModel()
        if self.sysmodel is None:
            return None
        return self.sysmodel

    def _modelFile(self, model):
        '''
        helper to return a SystemModelFile object
        '''
        return systemmodel.SystemModelFile(model)

    def _start_new_model(self):
        '''
        Start a new model with a mostly blank cfg
        '''
        # TODO
        self._new_cfg = conarycfg.ConaryConfiguration(False)
        self._new_cfg.initializeFlavors()
        self._new_cfg.dbPath = self._cfg.dbPath
        self._new_cfg.flavor = self._cfg.flavor
        self._new_cfg.configLine('updateThreshold 1')
        self._new_cfg.buildLabel = self._cfg.buildLabel
        self._new_cfg.installLabelPath = self._cfg.installLabelPath
        self._new_cfg.modelPath = '/etc/conary/system-model'
        model = cml.CML(self._new_cfg)
        model.setVersion(str(time.time()))
        newmodel = self._modelFile(model)
        return newmodel

    def _update_model(self, model, contents):
        '''
        Needs to be a system-model not a cml model
        '''
        self.system_model = contents
        model.parse(fileData=self.system_model)
        return model

    def _new_model(self):
        '''
        return a new model started using existing conary config
        '''
        cfg = self.conaryCfg
        model = cml.CML(cfg)
        model.setVersion(str(time.time()))
        newmodel = self._modelFile(model)
        return newmodel

    def _load_model_from_file(self, modelpath=None):
        '''
        Load model from /etc/conary/system-model unless modelpath
        is specified. If modelpath specified load file contents in
        the model before returning
        @param modelpath: Load a new model from a file location other
        than /etc/conary/system-model
        @type string
        '''
        contents = []
        if modelpath and os.path.exists(modelpath):
            try:
                contents = self.readStoredSystemModel(modelpath)
            except Exception, e:
                logger.error("FAILED TO READ MODEL : %s" % str(e))
                raise
        model = self._new_model()
        if contents:
            model = self._update_model(model, contents)
        return model

    def _load_model_from_string(self, modelData=None):
        model = self._new_model()
        if modelData:
            try:
                model = self._update_model(model, modelData)
            except Exception, e:
                #FIXME : Use a nice error...
                logger.error("FAILED TO READ MODEL : %s" % str(e))
                raise
        return model

    def _cleanSystemModel(self, modelFile):
        '''
        Clean up after applying the updates
        '''
        # copy snapshot to system-model
        #self.modelFile.closeSnapshot(fileName=modelFile.snapName)
        raise errors.NotImplementedError

    def _buildUpdateJob(self, model, modelFile, callback=None,
                                                changeSetList=[]):
        '''
        Build an update job from a system model
        @sysmod = SystemModelFile object
        @callback = UpdateCallback object
        return updJob, suggMapp
        '''
        cache = self._cache(callback)
        cclient = self._getClient(modelfile=modelFile)
        # Need to sync the capsule database before updating
        if cclient.cfg.syncCapsuleDatabase:
            cclient.syncCapsuleDatabase(callback)
        updJob = cclient.newUpdateJob()
        troveSetGraph = cclient.cmlGraph(model, changeSetList = changeSetList)
        try:
            suggMap = cclient._updateFromTroveSetGraph(updJob,
                            troveSetGraph, cache)
        except Exception, e:
            logger.error("FAILED %s" % str(e))
            if callback:
                callback.done()
            raise

        # LIFTED FROM updatecmd.py
        # TODO Remove the logger statements???
        finalModel = copy.deepcopy(model)
        if model.suggestSimplifications(cache, troveSetGraph.g):
            logger.info("possible system model simplifications found")
            troveSetGraph2 = cclient.cmlGraph(model)
            updJob2 = cclient.newUpdateJob()
            try:
                suggMap2 = cclient._updateFromTroveSetGraph(updJob2,
                                    troveSetGraph2, cache)
            except cerrors.TroveNotFound:
                logger.info("bad model generated; bailing")
            else:
                if (suggMap == suggMap2 and
                    updJob.getJobs() == updJob2.getJobs()):
                    logger.info("simplified model verfied; using it instead")
                    troveSetGraph = troveSetGraph2
                    finalModel = model
                    updJob = updJob2
                    suggMap = suggMap2
                else:
                    logger.info("simplified model changed result; ignoring")
        model = finalModel
        modelFile.model = finalModel

        if cache.cacheModified():
            logger.info("saving model cache to %s", self._model_cache_path)
            if callback:
                callback.savingModelCache()
            cache.save(self._model_cache_path)
            if callback:
                callback.done()

        return updJob, suggMap, model, modelFile

    def _applyUpdateJob(self, updJob, callback=None):
        '''
        Apply a thawed|current update job to the system
        '''
        updated = False
        jobs = updJob.getJobs()
        if callback:
            callback.executingSystemModel()
        if not jobs:
            return updated
            if callback:
                callback.done()
        try:
            cclient = self.conaryClient
            cclient.setUpdateCallback(callback)
            cclient.checkWriteableRoot()
            cclient.applyUpdateJob(updJob, noRestart=True)
            updated = True
        except Exception, e:
            raise errors.SystemModelServiceError, e
        if updated and callback:
            callback.done()
        return updated

    def _downloadUpdateJob(self, updJob, destDir, callback=None):
        downloaded = False
        jobs = updJob.getJobs()
        if not jobs:
            if callback:
                callback.done()
            return downloaded

        try:
            cclient = self.conaryClient
            cclient.setUpdateCallback(callback)
            cclient.downloadUpdate(updJob, destDir)
            downloaded = True
        except Exception, e:
            raise errors.SystemModelServiceError, e
        if downloaded and callback:
            callback.done()
        return downloaded

    def _freezeUpdateJob(self, updateJob, path):
        '''
        freeze an update job and store it on the filesystem
        '''
        frozen = False
        updateJob.freeze(path)
        frozen = True
        return frozen

    def _thawUpdateJob(self, path):
        if os.path.exists(path):
            cclient = self.conaryClient
            updateJob = cclient.newUpdateJob()
            updateJob.thaw(path)
        return updateJob

    def _getTopLevelItems(self):
        topLevelItems = [ trovetup.TroveTuple(x) for x
                    in self.conaryClient.getUpdateItemList() ]
        return sorted(topLevelItems)

    def _getTopLevelItemsFromUpdate(self, topTuples, updateJob):
        """
        Return the tuple for the new top-level group after applying an
        update job.
        """
        # TODO Decide how to handle multiple top level items
        # FIXME Hack this to support multiple top level items
        added = set()
        newTopTuples = set()
        topErased = False
        names = set(x.name for x in topTuples)
        for jobList in updateJob.getJobs():
            for (name, (oldVersion, oldFlavor), (newVersion, newFlavor),
                    isAbsolute) in jobList:
                if name in names:
                    if newVersion:
                        newTopTuples.add(trovetup.TroveTuple(name,
                                            newVersion, newFlavor))
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
                return [appliances[0]]
            else:
                # Pick any group
                return [sorted(added)[0]]
        # Not mentioned, so reuse the old version. Migrating to "remediate" a
        # system back to its nominal group would cause this, for example.
        return topTuples

    # OVERWRITE THESE FUNCTIONS

    def install(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def updateall(self):
        raise NotImplementedError

    def erase(self):
        raise NotImplementedError

    def preview(self, raiseExceptions=False):
        raise NotImplementedError

    def apply(self, raiseExceptions=False):
        raise NotImplementedError


class SyncModel(SystemModel):
    '''
    Sync to system-model destructive
    '''
    def __init__(self, modelfile=None, instanceid=None, callbackClass=None):
        super(SyncModel, self).__init__()
        self._newSystemModel = None
        self._modelfile = modelfile
        self.iid = instanceid
        # Setup flags
        self.flags = SystemModelFlags(apply=False, preview=False,
                freeze=False, thaw=False, iid=self.iid)

        # setup callback class
        if callbackClass is not None:
            self.callbackClass = callbackClass
        else:
            self.callbackClass = callbacks.UpdateCallback

    def _callback(self, job):
        return self.callbackClass(job)

    def _calculateDownloadSize(self, updateJob):
        serverBatch = {}
        sizes = []
        for jobs in updateJob.getJobs():
            for job in jobs:
                _, (oldVersion, _), (newVersion, _), _ = job
                oldHost = oldVersion.getHost() if oldVersion else None
                newHost = newVersion.getHost() if newVersion else None
                if oldHost != newHost and newHost is not None:
                    oldHost = None
                serverBatch.setdefault((oldHost, newHost), []).append(job)

        for (oldHost, newHost), jobs in serverBatch.iteritems():
            if oldHost is None:
                jobs = [(name, (None, None), newVersionFlavor, isAbsolute)
                        for name, _, newVersionFlavor, isAbsolute in jobs]
            sizes.append(
                sum(self.conaryClient.repos.getChangeSetSize(jobs)))
        return sum(sizes)

    def _getNewModelFromFile(self, modelfile):
        if not os.path.exists(modelfile):
            modelfile = '/etc/conary/system-model'
        return self._load_model_from_file(modelfile)

    def _getNewModelFromString(self, modelstring):
        return self._load_model_from_string(modelstring)

    def modelFilePath(self, dir):
        return os.path.join(os.path.dirname(dir), 'system-model')

    def thawSyncUpdateJob(self, job):
        updateJob = self._thawUpdateJob(job.updateJobDir)
        model = self._getNewModelFromString(job.systemModel)
        return updateJob, model

    def freezeSyncUpdateJob(self, updateJob, job):
        results = self._freezeUpdateJob(updateJob, job.updateJobDir)
        return results

    def _getPreviewFromUpdateJob(self, updateJob, observedTopLevelItems,
                                        desiredTopLevelItems, jobid=None):
        preview_xml = '<preview/>'
        preview = formatter.Formatter(updateJob)
        if preview:
            preview.format()
            for ntli in desiredTopLevelItems:
                preview.addDesiredVersion(ntli)
            for tli in observedTopLevelItems:
                preview.addObservedVersion(tli)
            if jobid:
                preview.addJobid(jobid)
            preview.addDownloadSize(self._calculateDownloadSize(updateJob))
            preview_xml = preview.toxml()
        return preview_xml

    def _prepareSyncUpdateJob(self, job, callback):
        '''
        Used to create an update job to make a preview from
        return job
        '''
        preview = None
        frozen = False
        jobid = job.keyId

        logger.info("BEGIN Sync update operation for job : %s" % jobid)

        # Top Level Items
        topLevelItems = self._getTopLevelItems()
        logger.info("Top Level Items")
        for n,v,f in topLevelItems:
            logger.info("%s %s %s" % (n,v,f))

        modelFile = self._getNewModelFromString(job.systemModel)
        model = modelFile.model

        if not job.systemModel:
            # we are doing a system update
            model.refreshVersionSnapshots()

        updateJob, suggMap, model, modelFile = self._buildUpdateJob(model, modelFile, callback)

        logger.info("Conary DB Transaction Counter: %s" % updateJob.getTransactionCounter())

        # update the job's system model with the newly calculated one
        job.systemModel = model.format()

        self.freezeSyncUpdateJob(updateJob, job)
        newTopLevelItems = self._getTopLevelItemsFromUpdate(topLevelItems,
                                                                updateJob)
        preview = self._getPreviewFromUpdateJob(updateJob, topLevelItems,
                                                    newTopLevelItems, jobid)
        return preview

    def _applySyncUpdateJob(self, job, callback):
        '''
        Used to apply a frozen job
        return a job
        '''
        jobid = job.keyId

        logger.info("BEGIN Applying sync update operation JOBID : %s" % jobid)
        # Top Level Items
        topLevelItems = self._getTopLevelItems()
        logger.info("Top Level Items")
        for n,v,f in topLevelItems: logger.info("%s %s %s" % (n,v,f))

        updateJob, model = self.thawSyncUpdateJob(job)
        job.state = "Applying"
        model.writeSnapshot()
        logger.info("Applying update job JOBID : %s from  %s"
                                % (jobid, job.updateJobDir))
        self._applyUpdateJob(updateJob, callback)

        model.closeSnapshot()
        newTopLevelItems = self._getTopLevelItems()
        logger.info("New Top Level Items")
        for n,v,f in newTopLevelItems:
            logger.info("%s %s %s" % (n,v,f))
        # Since we've just applied the update, the observed and desired
        # top level items are identical, which is usually not true for
        # previews
        preview = self._getPreviewFromUpdateJob(updateJob, newTopLevelItems,
                                                newTopLevelItems, jobid)
        return preview

    def _downloadSyncUpdateJob(self, job, callback):
        """
        Used to download the changeset for a frozen job
        """
        jobid = job.keyId

        logger.info("BEGIN Downloading changeset(s) for JOBID: %s" % jobid)
        updateJob, model = self.thawSyncUpdateJob(job)

        if updateJob.getChangesetsDownloaded():
            logger.info("Update already downloaded")
            return

        logger.debug('Deleting frozen update job')
        job.storage.delete((job.keyId, 'frozen-update-job'))
        job.state = "Downloading"
        logger.info("Downloading update job JOBID: %s to %s" %
                    (jobid, job.updateJobDir))
        downloaded = self._downloadUpdateJob(updateJob, job.downloadDir, callback)
        updateJob.setChangesetsDownloaded(downloaded)
        self.freezeSyncUpdateJob(updateJob, job)

    def _applyAction(self, action, job, endState, raiseExceptions):
        """
        Applies the action `action` to `job`
        """
        callback = self._callback(job)
        try:
            job.content = action(job, callback)
        except Exception as e:
            callback.done()
            job.content = str(e)
            job.state = "Exception"
            logger.error(job.content)
            if raiseExceptions:
                raise
            return None
        else:
            job.state = endState

        return job.content

    def preview(self, job, raiseExceptions=False):
        '''
        return preview
        '''
        return self._applyAction(self._prepareSyncUpdateJob, job,
                                 "Previewed", raiseExceptions)

    def apply(self, job, raiseExceptions=False):
        '''
        returns topLevelItems
        '''
        return self._applyAction(self._applySyncUpdateJob, job,
                                 "Applied", raiseExceptions)

    def download(self, job, raiseExceptions=False):
        return self._applyAction(self._downloadSyncUpdateJob, job,
                                 "Downloaded", raiseExceptions)

    def debug(self):
        #epdb.st()
        pass


class UpdateModel(SyncModel):
    def __init__(self, modelfile=None, instanceid=None):
        super(UpdateModel, self).__init__()
        self._newSystemModel = None
        self._modelfile = modelfile
        self.iid = instanceid
        # Setup flags
        self.flags = SystemModelFlags(apply=False, preview=False,
                freeze=False, thaw=False, iid=self.iid)


    def _newModelFile(self, model):
        newModelFile = "# Generated by rpath-tools \n"
        for x in model.modelOps:
            items = str(x.item)
            if isinstance(x.item, types.ListType):
                items = ' '.join(['"'+str(y)+'"' for y in x.item])
            newline = '''%s %s\n''' % (x.key,items)
            newModelFile = newModelFile + newline
        return newModelFile

    def _prepareUpdateUpdateJob(self, job, callback):
        '''
        Used to create an update job to make a preview from
        return job
        '''
        preview = None
        frozen = False
        jobid = job.keyId

        logger.info("BEGIN Update operation for job : %s" % jobid)

        # Top Level Items
        topLevelItems = self._getTopLevelItems()

        logger.info("Top Level Items")

        for n,v,f in topLevelItems:
            logger.info("%s %s %s" % (n,v,f))


        modelFile = self.conaryClient.getSystemModel()

        model = modelFile.model

        updates = [x for x in job.systemModel.split('\n')
                   if x and not x.startswith('#')]

        for update in updates:
            op, troveSpec = update.split(None, 1)
            model.appendOpByName(op, text=troveSpec)

        updateJob, suggMap, model, modelFile = self._buildUpdateJob(model, modelFile, callback)

        logger.info("Conary DB Transaction Counter: %s" % updateJob.getTransactionCounter())

        job.systemModel = self._newModelFile(model)

        self.freezeSyncUpdateJob(updateJob, job)
        newTopLevelItems = self._getTopLevelItemsFromUpdate(topLevelItems,
                                                                updateJob)
        preview = self._getPreviewFromUpdateJob(updateJob, topLevelItems,
                                                    newTopLevelItems, jobid)
        return preview

    def preview(self, job, raiseExceptions=False):
        '''
        return preview
        '''
        job_content = self._applyAction(self._prepareUpdateUpdateJob, job,
                                        "Previewed", raiseExceptions)
        return job_content



if __name__ == '__main__':
    import sys
    sys.excepthook = util.genExcepthook()

    fileName = sys.argv[1]
    try:
        with open(fileName) as f:
            blob=f.read()
    except EnvironmentError:
        print 'oops'


