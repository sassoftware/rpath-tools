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

from conary.conaryclient import cml
from conary.conaryclient import systemmodel
from conary.conaryclient import modelupdate
from conary.lib import util


from rpath_tools.lib import errors
from rpath_tools.lib import clientfactory
from rpath_tools.lib import callbacks
from rpath_tools.lib import updateset

import copy
import time
import os
import logging

logger = logging.getLogger(name = '__name__')



class UpdateFlags(object):
    __slots__ = [ 'migrate', 'update', 'updateall', 'sync', 'test',
                    'freeze', 'thaw', 'iid' ]
    def __init__(self, **kwargs):
        for s in self.__slots__:
            setattr(self, s, kwargs.pop(s, None))

class UpdateModel(object):
    def __init__(self, sysmod=None, callback=None):
        '''
        sysmod is a system-model string that will over write the current
        system-model.
        @param sysmod: A string representing the contents of a system-model file
        @type sysmod: String
        @param callback: A callback for messaging can be None
        @type callback: object like updatecmd.Callback
        '''
        self.conaryClientFactory = clientfactory.ConaryClientFactory
        self._sysmodel = None
        self._client = None
        self._newSystemModel = None
        self._contents = sysmod
        if self._contents:
            self._newSystemModel = [ x + '\n' for x in
                                        self._contents.split('\n') if x ]
        self._manifest = None
        self._cfg = self.conaryClientFactory.getCfg()
        self._callback = callback
        if not callback:
            self._callback = callbacks.UpdateCallback(
                                trustThreshold=self._cfg.trustThreshold)
        else:
            self._callback.setTrustThreshold(self._cfg.trustThreshold)

    @property
    def system_model(self):
        return self._newSystemModel

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
            return [ EnvironmentError, str(e) ]
        return data


    def _getClient(self, modelfile=None, force=False):
        if self._client is None or force:
            if self._system_model_exists():
                self._client = self.conaryClientFactory().getClient(
                                            modelFile=modelfile)
            else:
                self._client = self.conaryClientFactory().getClient(
                                            model=False)
        return self._client

    conaryClient = property(_getClient)

    def _getCfg(self):
        self._cfg = self.conaryClientFactory.getCfg()
        return self._cfg

    conaryCfg = property(_getCfg)

    def _system_model_exists(self):
        return os.path.isfile('/etc/conary/system-model')

    def _getSystemModel(self):
        cclient = self.conaryClient
        self.sysmodel = cclient.getSystemModel()
        if self.sysmodel is None:
            return None
        return self.sysmodel

    def _cleanSystemModel(self, modelFile):
        '''
        Clean up after applying the updates
        '''
        # copy snapshot to system-model
        #self.modelFile.closeSnapshot(fileName=modelFile.snapName)
        raise NotImplementedError

    def _cache(self, callback, changeSetList=[], loadTroveCache=True):
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
                    callback.loadingModelCache()
                    self._model_cache.load(self._model_cache_path)
            return self._model_cache
        except:
            return None

    def _troves(self):
        troves = self._model_cache.getTroves(
                [ x[0] for x in self._manifest ])
        return troves

    def _buildUpdateJob(self, sysmod, callback):
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
        except errors.TroveSpecsNotFound, e:
            print "FAILED %s" % str(e)
            callback.close()
            cclient.close()
            return updJob, {}

        # LIFTED FROM updatecmd.py
        # TODO Remove the logger statements???
        finalModel = copy.deepcopy(model)
        if model.suggestSimplifications(self._model_cache, troveSetGraph.g):
            logger.info("possible system model simplifications found")
            troveSetGraph2 = cclient.cmlGraph(model)
            updJob2 = cclient.newUpdateJob()
            try:
                suggMap2 = cclient._updateFromTroveSetGraph(updJob2,
                                    troveSetGraph2, self._model_cache)
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

        if self._model_cache.cacheModified():
            logger.info("saving model cache to %s", self._model_cache_path)
            callback.savingModelCache()
            self._model_cache.save(self._model_cache_path)
            callback.done()

        return updJob, suggMap

    def _applyUpdateJob(self, updJob, callback):
        '''
        Apply a thawed|current update job to the system
        '''
        updated = False
        jobs = updJob.getJobs()
        if not jobs:
            return updated
        try:
            cclient = self.conaryClient
            cclient.setUpdateCallback(callback)
            cclient.checkWriteableRoot()
            cclient.applyUpdateJob(updJob, noRestart=True)
            updated = True
        except Exception, e:
            raise errors.SystemModelServiceError, e
        return updated

    def _freezeUpdateJob(self, updateJob, model):
        '''
        freeze an update job and store it on the filesystem
        '''
        us = updateset.UpdateSet().new()
        key = us.keyId
        freezeDir = us.updateJobDir
        updateJob.freeze(freezeDir)
        return us, key

    def _thawUpdateJob(self, instanceId=None):
        if instanceId:
            keyId = instanceId.split(':')[1]
            job = updateset.UpdateSet().load(keyId)
        else:
            job = updateset.UpdateSet().latest()
            keyId = job.keyId

        cclient = self.conaryClient
        updateJob = cclient.newUpdateJob()
        updateJob.thaw(job.updateJobDir)
        return updateJob, job, keyId

    # FUTURE USE CODE.
    # Implement conary update, updateall, install, erase as it
    # correlates to a system model

    def _getTopLevelItems(self):
        return sorted(self.conaryClient.getUpdateItemList())

    def _getTransactionCount(self):
        db = self.conaryClient.getDatabase()
        return db.getTransactionCounter()

    def _system_model_update(self, cfg, op, args, callback, dry_run=False):
        '''
        conary update action for a system model
        op can be 'update'||'updateall'||'install'||'erase'.
        args is a list of packages.

        dry_run == True, return UpdateJob, suggMap
        '''

        updated = False
        updJob, suggMap = None, {}
        model = cml.CML(cfg)
        modelFile = systemmodel.SystemModelFile(model)
        model.appendOpByName(op, args)
        modelFile.writeSnapshot()
        try:
            updJob, suggMap = self._buildUpdateJob(model)
            #not sure i got this right... need  to just run an update
            #_model_build_update_job(cfg, model, modelFile, callback)
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


    def _startNew(self):
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
        return model

    def _modelFile(self, model):
        '''
        helper to return a SystemModelFile object
        '''
        return systemmodel.SystemModelFile(model)

    def _new_new_model(self):
        '''
        return a new model started using a blank conary config
        '''
        # TODO
        # Use this for converting a classic to systemmodel?
        # Use this during assimilation?
        model = self._startNew()
        model.setVersion(str(time.time()))

        # DON'T DO THIS... to low level
        #model.parse(fileData=self._newSystemModel, context=None)
        newmodel = self._modelFile(model)
        newmodel.parse(fileData=self.system_model)
        return newmodel

    def _new_model(self):
        '''
        return a new model started using existing conary config
        '''
        # TODO
        # Use this for converting a classic to systemmodel?
        # Use this during assimilation?
        #model = self._startNew()
        cfg = self.conaryCfg
        model = cml.CML(cfg)
        model.setVersion(str(time.time()))

        # DON'T DO THIS... to low level
        #model.parse(fileData=self._newSystemModel, context=None)
        newmodel = self._modelFile(model)
        newmodel.parse(fileData=self.system_model)
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
        cfg = self.conaryCfg
        if modelpath:
            contents = self.readStoredSystemModel(modelpath)
        model = cml.CML(cfg)
        model.setVersion(str(time.time()))
        # DON'T DO THIS... to low level
        #model.parse(fileData=self._newSystemModel, context=None)
        newmodel = self._modelFile(model)
        if contents:
            newmodel.parse(fileData=contents)
        return newmodel

    def _update_model(self, opargs):
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

    def update_model(self, opargs):
        # FIXME
        # Not sure what this is for yet...
        # Assuming public access to model for lib
        sysmod = self._update_model(opargs)
        return sysmod

    def new_model(self):
        # FIXME
        # This should be the function used for to
        # overwrite the system model using the system-model
        # from the rbuilder
        # Assuming public access to model for lib
        sysmod = self._new_model()
        return sysmod

    def sync(self):
        updated = False
        callback = self._callback
        flags = UpdateFlags(sync=True)
        instanceId, newTopLevelItems = self._prepareUpdateJob(flags)

    def preview(self):
        return

    def apply(self):
        return


class SyncModel(UpdateModel):
    def __init__(self, preview=False, apply=False, modelfile=None, instanceid=None):
        super(UpdateModel, self).__init__()
        self._newSystemModel = None
        self._model = None
        self.preview = preview
        self.apply = apply
        self.iid = instanceid
        self.thaw = False
        if self.iid:
            self.thaw = True
        # Setup flags
        self.flags = UpdateFlags(apply=self.apply, preview=self.preview,
                freeze=True, thaw=self.thaw, iid=self.iid)
        if modelfile and os.path.exists(modelfile):
            self._newSystemModel = self.readStoredSystemModel(modelfile)
            # New System Model
            self._model = self.new_model()


    def tcountFile(self, key):
        return os.path.join(dirName, 'transactionCounter.%s' % key)

    def thawSyncUpdateJob(self, instanceid):
        updateJob, updateSet, key = self._thawUpdateJob(instanceId=instanceid)
        fileName = os.path.join(os.path.dirname(updateSet.updateJobDir),
                                            'system-model.%s' % key)
        model = self._load_model_from_file(modelpath=fileName)
        tcountFile = os.path.join(dirName, 'transactionCounter.%s' % key)
        tcount = self.readStoredFile(tcountFile)
        return updateJob, updateSet, model, tcount

    def freezeSyncUpdateJob(self, updateJob, model, tcount, callback):
        us, key = self._freezeUpdateJob(updateJob, callback)
        instanceId = 'updates:%s' % key
        ##epdb.st()
        # FIXME
        # Store the system model with the updJob
        dirName = os.path.dirname(us.updateJobDir)
        fileName = os.path.join(dirName, 'system-model.%s' % key)
        model.write(fileName=fileName)
        tcountFile = os.path.join(dirName, 'transactionCounter.%s' % key)
        results, fd = self.storeInFile(tcount, tcountFile)
        ##epdb.st()
        return us, instanceId

    def _prepareSyncUpdateJob(self):
        '''
        Used to create an update job to make a preview from
        '''
        preview = None
        callback = self._callback
        # Transaction Counter
        tcount = self._getTransactionCount()
        print "Conary DB Transaction Counter: %s" % tcount

        # Top Level Items
        topLevelItems = self._getTopLevelItems()
        print "Top Level Items"
        for n,v,f in topLevelItems: print "%s %s %s" % (n,v,f)

        updateSet = {}

        ##epdb.st()
        updateJob, suggMap = self._buildUpdateJob(model, callback)
        ##epdb.st()

        if self.flags.freeze:
            updateSet, instanceId = self.freezeUpdateJob(updateJob, model,
                                                    tcount, callback)

        if self.flags.preview:
            preview = fmt.toxml(updateJob)
        #else:
            # FIXME
            #preview = topLevelItems.toxml(tcount)

        return updateJob, updateSet, instanceId, preview

    def _applySyncUpdateJob(self, instanceid=None):
        '''
        Used to apply a frozen job
        '''
        updated = False
        callback = self._callback
        # Top Level Items
        topLevelItems = self._getTopLevelItems()
        print "Top Level Items"
        for n,v,f in topLevelItems: print "%s %s %s" % (n,v,f)

        if instanceid:
            self.flags.iid = instanceid
        elif self.flags.iid:
            instanceid = self.flags.iid

        # FIXME
        # This is always going to be true
        if self.flags.thaw:
            updJob, updateSet, model, tcount = self.thawSyncUpdateJob(instanceid)
            #epdb.st()
            try:
                updateSet.state = "Applying"
                model.writeSnapshot()
                # NEED THIS  LATER·WHEN INVOKED BY CIM
                #self._fixSignals()
                #epdb.st()
                # SILLY CODE FOR MISA
                ctcount = self._getTransactionCount()

                if str(tcount.strip()) == str(ctcount):
                    self._applyUpdateJob(updJob, callback)
                    updated = True
                else:
                    print "Transaction count changed!!!"
                    updated = False
            except Exception, e:
                print "FAILED: %s" % str(e)
                updated = False
        if updated:
            model.closeSnapshot()
            topLevelItems = self._getTopLevelItems()
            print "New Top Level Items"
            for n,v,f in topLevelItems: print "%s %s %s" % (n,v,f)

        return instanceid, topLevelItems

    def previewSyncOperation(self, modelfile=None, preview=None):
        if modelfile and os.path.exists(modelfile):
            self._newSystemModel = self.readStoredSystemModel(modelfile)
        if preview:
            self.flags.preview = preview
        updateJob, updateSet, instanceId, preview = self._prepareSyncUpdateJob()
        return updateJob, updateSet, instanceId, preview

    def applySyncOperation(self, instanceid=None):
        instanceid, topLevelItems = self._applySyncUpdateJob(instanceid)
        return instanceid, topLevelItems

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

    sysmod = SyncModel(fileName)
    sysmod.debug()
