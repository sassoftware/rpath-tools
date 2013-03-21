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


from conary import callbacks
from conary import updatecmd
#from conary import command
from conary import conarycfg
#from coanry import constants
from conary import conaryclient
from conary import errors
from conary.conaryclient import cml
from conary.conaryclient import systemmodel
from conary.conaryclient import modelupdate
#from conary.errors import ParseError
#from conary.errors import TroveSpecsNotFound
from conary.lib import util

from sysmodel import SystemModel

import copy
import time
import os
import subprocess
import logging
import stored_objects

logger = logging.getLogger(name = '__name__')

#from conary.lib import debugger as epdb

class SystemModelServiceError(Exception):
    "Base class"

class NoUpdatesFound(SystemModelServiceError):
    "Raised when no updates are available"

class RepositoryError(SystemModelServiceError):
    "Raised when a repository error is caught"

class ConaryClientFactory(object):
    def getClient(self, modelFile=None):
        ccfg = conarycfg.ConaryConfiguration(readConfigFiles=True)
        ccfg.initializeFlavors()
        if modelFile:
            cclient = conaryclient.ConaryClient(ccfg, modelFile=modelFile)
        else:
            model = cml.CML(ccfg)
            modelFile = systemmodel.SystemModelFile(model)
            cclient = conaryclient.ConaryClient(ccfg)
        callback = updatecmd.callbacks.UpdateCallback()
        cclient.setUpdateCallback(callback)
        return cclient

class UpdateFlags(object):
    __slots__ = [ 'migrate', 'update', 'updateall', 'sync', 'test', 'freeze' ]
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
        self.conaryClientFactory = ConaryClientFactory
        self._sysmodel = None
        self._client = None
        self._newSystemModel = None
        self._contents = sysmod
        if self._contents:
            self._newSystemModel = [ x + '\n' for x in
                                        self._contents.split('\n') if x ]
        self._manifest = None
        self._cfg = conarycfg.ConaryConfiguration(True)
        self._callback = callback
        if not callback:
            self._callback = callbacks.UpdateCallback(
                                trustThreshold=self._cfg.trustThreshold)
        else:
            self._callback.setTrustThreshold(self._cfg.trustThreshold)
        #self._client = conaryclient.ConaryClient(self._cfg)

    @property
    def system_model(self):
        return self._newSystemModel

    def _runProcess(self, cmd):
        '''cmd @ [ '/sbin/service', 'name', 'status' ]'''
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

    def _getClient(self, modelfile=None, force=False):
        if self._client is None or force:
            if self._system_model_exists():
                self._client = self.conaryClientFactory().getClient(
                                            modelFile=modelfile)
        return self._client

    conaryClient = property(_getClient)

    def _getCfg(self):
        self._cfg = conarycfg.ConaryConfiguration(readConfigFiles=True)
        self._cfg.initializeFlavors()
        return self._cfg

    conaryCfg = property(_getCfg)

    def _system_model_exists(self):
        return os.path.isfile('/etc/conary/system-model')

    def _getSystemModel(self):
        cclient = self.conaryClient
        self.sysmodel = cclient.getSystemModel()
        if self.sysmodel is None:
            return None
        return SystemModel(self.sysmodel)

    def _cleanSystemModel(self, modelFile):
        '''
        Clean up after applying the updates
        '''
        # copy snapshot to system-model
        self.modelFile.closeSnapshot(fileName=modelFile.snapName)
        pass

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
            return
        try:
            cclient = self.conaryClient
            cclient.setUpdateCallback(callback)
            cclient.checkWriteableRoot()
            cclient.applyUpdateJob(updJob, noRestart=True)
            updated = True
        except Exception, e:
            # FIXME this should puke...
            return SystemModelServiceError, e
        return updated

    def _freezeUpdateJob(self, updateJob, model):
        '''
        freeze an update job and store it on the filesystem
        '''
        us = UpdateSet().new()
        key = us.keyId
        freezeDir = us.updateJobDir
        updateJob.freeze(freezeDir)
        return us, key

    def _thawUpdateJob(self, instanceId=None):
        if instanceId:
            keyId = instanceId.split(':')[1]
            job = UpdateSet().load(keyId)
        else:
            job = UpdateSet().latest()
            keyId = job.keyId

        cclient = self.conaryClient
        updateJob = cclient.newUpdateJob()
        updateJob.thaw(job.updateJobDir)
        return keyId, updateJob, job

    # FUTURE USE CODE.
    # Implement conary update, updateall, install, erase as it
    # correlates to a system model

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
        # DO we really need this?
        newFileExt = '.new'
        fileName = self._cfg.modelPath + newFileExt
        self._new_cfg = conarycfg.ConaryConfiguration(False)
        self._new_cfg.initializeFlavors()
        self._new_cfg.dbPath = self._cfg.dbPath
        self._new_cfg.flavor = self._cfg.flavor
        self._new_cfg.configLine('updateThreshold 1')
        self._new_cfg.buildLabel = self._cfg.buildLabel
        self._new_cfg.installLabelPath = self._cfg.installLabelPath
        self._new_cfg.modelPath = fileName
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
        newmodel = SystemModel(self._modelFile(model))
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
        newmodel = SystemModel(self._modelFile(model))
        newmodel.parse(fileData=self.system_model)
        return newmodel

    def _load_model_from_file(self, modelpath=None):
        cfg = self.conaryCfg
        if modelpath:
            cfg.modelPath = modelpath
        model = cml.CML(cfg)
        model.setVersion(str(time.time()))
        # DON'T DO THIS... to low level
        #model.parse(fileData=self._newSystemModel, context=None)
        newmodel = SystemModel(self._modelFile(model))
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
        newmodel = SystemModel(self._modelFile(model))
        return newmodel

    def update_model(self):
        # FIXME
        # Not sure what this is for yet...
        # Assuming public access to model for lib
        sysmod = self._update_model()
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
        # FIXME: REMOVE AT SOME POINT
        # Nasty command line call for testing and debug
        # Try not to ever usee this
        cmd = [ 'conary' , 'sync' ]
        results = self._runProcess(cmd)
        return results

    def debug(self):
        updated = False
        callback = self._callback
        flags = UpdateFlags(sync=True, freeze=True, migrate=False,
                                update=False, updateall=False,
                                test=True, )
        # Current System Model
        #model = self._getSystemModel()
        # Updated Current model Not implemented yet
        #model = self.update_model()
        # New System Model
        model = self.new_model()
        updateJob, suggMap = self._buildUpdateJob(model, callback)
        if flags.freeze:
            us, key = self._freezeUpdateJob(updateJob, callback)
            # FIXME
            # Store the system model with the updJob
            fileName = os.path.join(os.path.dirname(us.updateJobDir),
                                            'system-model.%s' % key)
            model.write(fileName=fileName)
        if flags.test:
            pass
        if flags.sync:
            instanceId = 'updates:%s' % key
            keyId, updJob, updateSet = self._thawUpdateJob(instanceId=instanceId)
            try:
                updateSet.state = "Applying"
                self._fixSignals()
                self._applyUpdateJob(updJob, callback)
                updated = True
            except Exception, e:
                print "FAILED: %s" % str(e)
                updated = False
        if updated:
            # TODO: system-model
            # I need to dig up  the  model here...
            # create a model from the system-model file
            # in the frozen directory return it so
            # we can write it after update succeeds
            # Load the system-model from storage
            fileName = os.path.join(os.path.dirname(updJob.updateJobDir),
                                            'system-model.%s' % updJob.keyId)
            updated_model = self._load_model_from_file(modelFile=fileName)
            updated_model.write(modelFile='/etc/conary/system-model')

        #import epdb;epdb.st()

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

class UpdateSet(object):
    storagePath = "/var/lib/conary-cim/storage"

    factory = stored_objects.UpdateSetFactory

    def __init__(self):
        self.updateSet = None

    def new(self):
        self.updateSet = self.factory(self.storagePath).new()
        return self

    @classmethod
    def latestFilter(cls, obj):
        return obj.state != "Applying"

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

    def _getKeyId(self):
        return self.updateSet.keyId

    keyId = property(_getKeyId)

    def _getUpdateJobDir(self):
        return self.updateSet.updateJobDir

    updateJobDir = property(_getUpdateJobDir)


if __name__ == '__main__':
    import sys
    sys.excepthook = util.genExcepthook()

    fileName = sys.argv[1]
    try:
        with open(fileName) as f:
            blob=f.read()
    except EnvironmentError:
        print 'oops'

    sysmod = UpdateModel(blob)
    sysmod.debug()
