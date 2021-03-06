#!/usr/conary/bin/python2.6
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


import itertools
import optparse
import os
import shutil
import subprocess
import sys
import traceback

from rpath_tools.lib import stored_objects
from rpath_tools.lib import installation_service, update

class TaskRunner(object):
    def runAsync(self, task, *args, **kwargs):
        task.job.state = "Starting"

        self.background_run(self.runSync, task, args, kwargs)
        return task

    def runSync(self, task, *args, **kwargs):
        job = task.job
        job.pid = os.getpid()
        job.state = "Running"

        try:
            task.run(*args, **kwargs)
        except Exception:
            job.content = traceback.format_exc()
            job.state = "Exception"
        else:
            job.state = "Completed"

    def background_run(self, function, task, args, kwargs):
        task.preFork(*args, **kwargs)
        pid = os.fork()
        if pid:
            os.waitpid(pid, 0)
            return
        try:
            try:
                pid = os.fork()
                if pid:
                    # The first child exits and is waited by the parent
                    # the finally part will do the os._exit
                    return
                task.postFork(*args, **kwargs)
                # Redirect stdin, stdout, stderr
                fd = os.open(os.devnull, os.O_RDWR)
                os.dup2(fd, 0)
                os.dup2(fd, 1)
                os.dup2(fd, 2)
                os.close(fd)
                # Create new process group
                os.setsid()

                os.chdir('/')
                function(task, *args, **kwargs)
            except Exception:
                try:
                    ei = sys.exc_info()
                    self.log_error('Daemonized process exception',
                                   exc_info = ei)
                finally:
                    os._exit(1)
        finally:
            os._exit(0)


class BaseTask(object):
    storagePath = installation_service.InstallationService.UpdateSetFactory.storagePath
    jobFactory = None
    TaskRunner = TaskRunner
    def __init__(self):
        self.concreteJob = None

    def new(self):
        self.job = self.jobFactory(self.storagePath).new()
        self.job.state = "New"
        return self

    def load(self, jobId):
        self.job = self.jobFactory(self.storagePath).load(self.sanitizeKey(jobId))
        return self

    def get_job_id(self):
        return self.job.keyId

    def list(self):
        return [ x for x in self.jobFactory(self.storagePath) ]

    @property
    def logs(self):
        return self.job.logs

    def __call__(self, *args, **kwargs):
        """
        Asyncrhonously invoke the run method via the TaskRunner
        """
        runner = self.TaskRunner()
        return runner.runAsync(self, *args, **kwargs)

    def run(self, *args, **kwargs):
        """
        Method invoked by the task runner after detaching
        """
        raise NotImplemented

    def preFork(self, *args, **kwargs):
        """
        Method invoked before the task runner forks.
        The arguments and keyword arguments are the same as the ones passed to
        the run method.
        """

    def postFork(self, *args, **kwargs):
        """
        Method invoked after the task runner forks.
        The arguments and keyword arguments are the same as the ones passed to
        the run method.
        """

    @classmethod
    def sanitizeKey(cls, jobId):
        return jobId

    def cleanJob(self):
        for key in self.job.storage.enumerateAll():
            self.job.storage.delete(key)

class BaseUpdateTask(BaseTask):
    jobFactory = stored_objects.ConcreteUpdateJobFactory

    def cleanJob(self):
        super(BaseUpdateTask, self).cleanJob()
        shutil.rmtree(os.path.join(
            self.job.storage.cfg.storagePath, self.job.keyId))

class UpdateCheckTask(BaseUpdateTask):
    def run(self):
        instserv = installation_service.InstallationService()
        instserv.updateAllCheck()

class UpdateAllTask(BaseUpdateTask):
    def run(self, instanceId):
        instserv = installation_service.InstallationService()
        instserv.updateAllApply(instanceId)

class UpdateTask(BaseUpdateTask):
    def run(self, sources, flags):
        instserv = installation_service.InstallationService()
        self.job.content = instserv.updateOperation(self.job, sources, flags)

class SyncPreviewTask(BaseUpdateTask):
    def preFork(self, systemModelPath, flags=None):
        self.job.systemModel = file(systemModelPath).read()

    def postFork(self, *args, **kwargs):
        update.SyncModel.fixSignals()

    def run(self, systemModelPath, flags=None):
        operation = update.SyncModel()
        operation.preview(self.job, raiseExceptions=True)

class SyncApplyTask(BaseUpdateTask):
    def postFork(self, *args, **kwargs):
        update.SyncModel.fixSignals()

    def run(self, flags=None):
        operation = update.SyncModel()
        operation.apply(self.job, raiseExceptions=True)

    @classmethod
    def sanitizeKey(cls, key):
        return (cls.jobFactory.factory.keyPrefix,
                key.rsplit('/', 1)[-1])

class UpdatePreviewTask(BaseUpdateTask):
    def preFork(self, systemModelPath, flags=None):
        self.job.systemModel = file(systemModelPath).read()

    def postFork(self, *args, **kwargs):
        update.SyncModel.fixSignals()

    def run(self, systemModelPath, flags=None):
        operation = update.UpdateModel()
        operation.preview(self.job, raiseExceptions=True)

class DownloadTask(BaseUpdateTask):
    def postFork(self, *args, **kwargs):
        update.SyncModel.fixSignals()

    def run(self, flags=None):
        operation = update.SyncModel()
        operation.download(self.job, raiseExceptions=True)


class AnyTask(object):
    # XXX Make this more extensible
    _allClasses = [ UpdateTask, ]

    @classmethod
    def list(cls):
        return itertools.chain(*(cls().list() for cls in cls._allClasses))

    @classmethod
    def load(cls, keyId):
        for klass in cls._allClasses:
            if keyId.startswith(klass.jobFactory.factory.keyPrefix + '/'):
                return klass().load(keyId)
        return None

def startUpdateOperation(sources, flags):
    task = UpdateTask().new()
    task(sources, flags)
    return task

def reexec(args):
    pythonExec = os.path.join(sys.exec_prefix, "bin", "python")
    execPath = __file__
    callArgs = [ pythonExec, execPath ] + args

    # Use subprocess to start the update job.  jobs.py double forks,
    # so the wait will return almost immediately.
    jobProc = subprocess.Popen(callArgs, stdout=subprocess.PIPE)
    jobProc.wait()
    return jobProc

def main():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--test", action="store_true", dest="test")
    parser.add_option("-m", "--mode", action="store", type="choice",
        choices=["update", "updateall", "migrate", "sync"], dest="mode")
    parser.add_option("-p", "--package", action="append", dest="package")
    parser.add_option("--system-model-path", action="store", dest="systemModelPath")
    parser.add_option("--update-id", action="store", dest="updateId")
    (options, args) = parser.parse_args()

    kwargs = {}

    if not options.mode:
        sys.exit(-1)

    if not options.package and not options.systemModelPath and not options.updateId:
        sys.exit(-1)

    kwargs[options.mode] = True
    kwargs['test'] = bool(options.test)

    flags = installation_service.InstallationService.UpdateFlags(**kwargs)
    if options.package:
        task = startUpdateOperation(sources=options.package, flags=flags)
    elif options.systemModelPath:
        task = SyncPreviewTask().new()
        task(options.systemModelPath, flags)
    elif options.updateId:
        task = SyncApplyTask().load(options.updateId)
        task(flags)
    print task.get_job_id()
    sys.exit()

if __name__ == "__main__":
    main()
