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
from conary import trovetup

from conary.conaryclient import cml
from conary.conaryclient import systemmodel
from conary.conaryclient import modelupdate
from conary.lib import util


from rpath_tools.lib import errors
from rpath_tools.lib import clientfactory
from rpath_tools.lib import callbacks
from rpath_tools.lib import stored_objects
from rpath_tools.lib import formatter

import copy
import types
import time
import os
import logging
import traceback

logger = logging.getLogger(name = '__name__')



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

    def _getClient(self, modelfile=None, force=False):
        if self._cclient is None or force:
            if self._system_model_exists():
                self._cclient = self.conaryClientFactory().getClient(
                                            modelFile=modelfile)
            else:
                self._cclient = self.conaryClientFactory().getClient(
                                            model=False)
        return self._cclient

    conaryClient = property(_getClient)

    def _getCfg(self):
        self._cfg = self.conaryClientFactory().getCfg()
        return self._cfg

    conaryCfg = property(_getCfg)

    def _system_model_exists(self):
        cfg = self.conaryClientFactory().getCfg()
        return os.path.isfile(cfg.modelPath)

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
            #FIXME
            raise EnvironmentError, str(e)
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
                #raise Exception, str(e)
        return model


    def _cleanSystemModel(self, modelFile):
        '''
        Clean up after applying the updates
        '''
        # copy snapshot to system-model
        #self.modelFile.closeSnapshot(fileName=modelFile.snapName)
        raise errors.NotImplementedError


    def _buildUpdateJob(self, sysmod, callback=None):
        '''
        Build an update job from a system model
        @sysmod = SystemModelFile object
        @callback = UpdateCallback object
        return updJob, suggMapp
        '''

        model = sysmod.model
        cache = self._cache(callback)
        cclient = self._getClient(modelfile=sysmod)
        # Need to sync the capsule database before updating
        if cclient.cfg.syncCapsuleDatabase:
            cclient.syncCapsuleDatabase(callback)
        updJob = cclient.newUpdateJob()
        troveSetGraph = cclient.cmlGraph(model)
        try:
            suggMap = cclient._updateFromTroveSetGraph(updJob,
                            troveSetGraph, cache)
        except Exception, e:
            logger.error("FAILED %s" % str(e))
            if callback:
                callback.done()
            return updJob, {}

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
            except errors.TroveNotFound:
                logger.info("bad model generated; bailing")
                pass
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
        sysmod.model = finalModel

        if cache.cacheModified():
            logger.info("saving model cache to %s", self._model_cache_path)
            if callback:
                callback.savingModelCache()
            cache.save(self._model_cache_path)
            if callback:
                callback.done()

        return updJob, suggMap

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

    def _freezeUpdateJob(self, updateJob, path):
        '''
        freeze an update job and store it on the filesystem
        '''
        frozen = False
        try:
            updateJob.freeze(path)
            frozen = True
        except Exception, e:
            # FIXME still wrong... 
            raise errors.FrozenUpdateJobError, errors.FrozenUpdateJobError(e)
        return frozen

    def _thawUpdateJob(self, path):
        if os.path.exists(path):
            try:
                cclient = self.conaryClient
                updateJob = cclient.newUpdateJob()
                updateJob.thaw(path)
            except:
                # FIXME
                raise errors.FrozenJobPathMissing
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
        names = [ x.name for x in topTuples ]
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
                return appliances[0]
            else:
                # Pick any group
                return sorted(added)[0]
        # Not mentioned, so reuse the old version. Migrating to "remediate" a
        # system back to its nominal group would cause this, for example.
        return topTuples
 
    def _getTransactionCount(self):
        db = self.conaryClient.getDatabase()
        return db.getTransactionCounter()

    # OVERWRITE THESE FUNCTIONS

    def install(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def updateall(self):
        raise NotImplementedError

    def erase(self):
        raise NotImplementedError

    def preview(self):
        raise NotImplementedError

    def apply(self):
        raise NotImplementedError


class UpdateModel(SystemModel):
    '''
    Update the current system-model non destructive
    '''
    def __init__(self, preview=False, apply=False,
                        modelfile=None, instanceid=None):
        super(UpdateModel, self).__init__()
        # New System Model
        self._newSystemModel = None
        self._model = None
        self.preview = preview
        self.apply = apply
        self.iid = instanceid
        self.thaw = True
        # Setup flags
        self.flags = SystemModelFlags(apply=self.apply, preview=self.preview,
                freeze=True, thaw=self.thaw, iid=self.iid)

    def _load_model_with_list_of_tuples(self, opargs):
        '''
        Updated system model from current system model
        @param opargs: a list of tuples of operation and a tuple
        of packages that go with the operation
        ie: [ ('install'('lynx', 'joe')),
                ('remove', ('httpd')),
                ('update', ('wget')),
                ]
        @type opargs: list of tuples [(op, args)]
        @param op: a conary system model operation 'install', 'update', 'erase'
        @type op: string
        @param args: a tuple of conary packages for an operation 
        @type args: ( pkg1, pkg2 )
        @param pkg: a name of a conary package
        @type pkg: string
        @return: conary SystemModelFile object
        '''
        # FIXME
        # This should append to the current system-model
        # need a dictionary of { op : arg } to parse
        cfg = self.conaryCfg
        model = cml.CML(cfg)
        model.setVersion(str(time.time()))
        # I think this is how it should work
        # Take some uglies from stdin and append them
        # to current system model
        # apparently in the most ugly way I can
        for op, args in opargs.items():
            arg = ' '.join([ x for x in args ])
            model.appendOpByName(op, arg)
        newmodel = self._modelFile(model)
        return newmodel

    def _system_model_update(self, cfg, op, args, callback, dry_run=False):
        '''
        conary update action for a system model
        op can be 'update'||'updateall'||'install'||'erase'.
        args is a list of packages.

        dry_run == True, return UpdateJob, suggMap
        '''
        # FIXME
        # FUTURE CODE THAT IS A MESS
        updated = False
        updJob, suggMap = None, {}
        model = cml.CML(cfg)
        modelFile = systemmodel.SystemModelFile(model)
        model.appendOpByName(op, args)
        modelFile.writeSnapshot()
        try:
            updJob, suggMap = self._buildUpdateJob(model)
            if not dry_run:
                self._applyUpdateJob(updJob, callback)
                updated = True
        except:
            pass
        if updated:
            modelFile.write()
            modelFile.closeSnapshot()
        return updJob, suggMap

    def _base_update(self, arg, pkglist, callback, dry_run):
        '''
        update helper so I don't have to repeat code
        '''
        cfg = self.conaryCfg
        updJob, suggMap = None, {}
        if self._using_system_model():
            updJob, suggMap = self._system_model_update(cfg,
                                arg, pkglist, callback, dry_run)
        return updJob, suggMap

    def update(self, pkglist, callback, dry_run=False):
        '''
        conary install for system model
        '''
        cfg = self.conaryCfg
        updJob, suggMap = None, {}
        if self._using_system_model():
            updJob, suggMap = self._system_model_update(cfg,
                                'update', pkglist,
                    callback, dry_run)
        return updJob, suggMap


    def install(self, pkglist, callback, dry_run=False):
        '''
        conary install for system model
        return updJob, suggMap
        '''
        return self._base_updater('install', pkglist,
                                callback, dry_run)


    def erase(self, pkglist, callback, dry_run=False):
        '''
        conary erase for system model
        return updJob, suggMap
        '''
        return self._base_updater('erase', pkglist,
                                callback, dry_run)

    def updateall(self, pkglist=[], dry_run=False):
        '''
        conary updateall for system model
        return updJob, suggMap
        '''
        return self._base_updater('updateall', pkglist,
                                 dry_run)


    def sync(self):
        return NotImplementedError

    def preview(self):
        return NotImplementedError

    def apply(self):
        return NotImplementedError


class SyncModel(SystemModel):
    '''
    Sync to system-model destructive
    '''
    def __init__(self, modelfile=None, instanceid=None):
        super(SyncModel, self).__init__()
        self._newSystemModel = None
        self._modelfile = modelfile
        self.iid = instanceid
        # Setup flags
        self.flags = SystemModelFlags(apply=False, preview=False,
                freeze=False, thaw=False, iid=self.iid)

    def _callback(self, job):
        return callbacks.UpdateCallback(job)

    def _getNewModelFromFile(self, modelfile):
        if modelfile and os.path.exists(modelfile):
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

    def _getPreviewFromUpdateJob(self, updateJob, topLevelItems,
                                        newTopLevelItems, jobid=None):
        preview_xml = '<preview/>'
        preview = formatter.Formatter(updateJob)
        if preview:
            preview.format()
            for ntli in newTopLevelItems:
                preview.addDesiredVersion(ntli)
            for tli in topLevelItems:
                preview.addObservedVersion(tli)
            if jobid:
                preview.addJobid(jobid)
            preview_xml = preview.toxml()
        return preview_xml

    def _prepareSyncUpdateJob(self, job):
        '''
        Used to create an update job to make a preview from
        return job
        '''
        preview = None
        frozen = False
        callback = self._callback(job)
        jobid = job.keyId

        logger.info("BEGIN Sync update operation for job : %s" % jobid)
        # Transaction Counter
        tcount = self._getTransactionCount()
        logger.info("Conary DB Transaction Counter: %s" % tcount)

        # Top Level Items
        topLevelItems = self._getTopLevelItems()
        logger.info("Top Level Items")
        for n,v,f in topLevelItems:
            logger.info("%s %s %s" % (n,v,f))

        model = self._getNewModelFromString(job.systemModel)

        updateJob, suggMap = self._buildUpdateJob(model, callback)

        # TODO : REVIEW if self.flags helps...
        # SILLY AS IT IS ALWAYS TRUE
        # And with returning a job I have to freeze the update
        if self.flags.freeze:
            try:
                frozen = self.freezeSyncUpdateJob(updateJob, job)
            except Exception, e:
                # FIXME
                job.content = traceback.format_exc()
                job.state = "Exception"
                logger.error("JOBID : %s FAILED: %s" % (jobid, str(e)))
                if callback:
                    callback.done()
                return job
        # TODO : REVIEW if self.flags helps...
        # SILLY AS IT IS ALWAYS TRUE
        # I should probably remove self.flags cause it is overkill
        if self.flags.preview:
            newTopLevelItems = self._getTopLevelItemsFromUpdate(topLevelItems,
                                                                    updateJob)
            preview = self._getPreviewFromUpdateJob(updateJob, topLevelItems,
                                                        newTopLevelItems, jobid)
            if preview:
                job.content = preview
        if frozen:
            job.state = "Frozen"
        return job



    def _applySyncUpdateJob(self, job):
        '''
        Used to apply a frozen job
        return a job
        '''
        callback = self._callback(job)
        jobid = job.keyId

        logger.info("BEGIN Applying sync update operation JOBID : %s" % jobid)
        # Top Level Items
        topLevelItems = self._getTopLevelItems()
        logger.info("Top Level Items")
        for n,v,f in topLevelItems: logger.info("%s %s %s" % (n,v,f))

        updateJob, model = self.thawSyncUpdateJob(job)
        try:
            job.state = "Applying"
            model.writeSnapshot()
            logger.info("Applying update job JOBID : %s from  %s"
                                    % (jobid, job.updateJobDir))
            self._applyUpdateJob(updateJob, callback)
        except Exception, e:
            job.content = traceback.format_exc()
            job.state = "Exception"
            logger.error("JOBID : %s FAILED: %s" % (jobid, str(e)))
            if callback:
                callback.done()
            return job

        model.closeSnapshot()
        newTopLevelItems = self._getTopLevelItems()
        logger.info("New Top Level Items")
        for n,v,f in newTopLevelItems:
            logger.info("%s %s %s" % (n,v,f))
        preview = self._getPreviewFromUpdateJob(updateJob, topLevelItems,
                                                    newTopLevelItems, jobid)
        if preview:
            job.content = preview
        job.state = "Completed"
        logger.info("Completed apply for sync update operation JOBID : %s" % jobid)
        return job

    def preview(self, job):
        '''
        return preview
        '''
        # Always run a preview when calling preview
        # unless you mean not run a preview
        self.flags.preview = True
        self.flags.freeze = True
        job = self._prepareSyncUpdateJob(job)
        return job.content

    def apply(self, job):
        '''
        returns topLevelItems
        '''
        self.flags.apply = True
        self.flags.thaw = True
        job = self._applySyncUpdateJob(job)
        return job.content

    def debug(self):
        #epdb.st()
        pass

if __name__ == '__main__':
    import sys
    sys.excepthook = util.genExcepthook()

    fileName = sys.argv[1]
    try:
        with open(fileName) as f:
            blob=f.read()
    except EnvironmentError:
        print 'oops'


