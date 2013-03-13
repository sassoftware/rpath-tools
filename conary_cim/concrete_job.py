#!/usr/bin/python2.6
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
import sys
import traceback

import stored_objects
import surveys
import installation_service

class BaseJob(object):
    storagePath = None
    factory = None
    def __init__(self):
        self.concreteJob = None

    def new(self):
        self.concreteJob = self.factory(self.storagePath).new()
        self.concreteJob.state = "New"
        return self

    def load(self, jobId):
        self.concreteJob = self.factory(self.storagePath).load(jobId)
        return self

    def get_job_id(self):
        return self.concreteJob.keyId

    def list(self):
        return [ x for x in self.factory(self.storagePath) ]

    @property
    def logs(self):
        return self.concreteJob.logs

    def background_run(self, function, *args, **kw):
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
                # Redirect stdin, stdout, stderr
                fd = os.open(os.devnull, os.O_RDWR)
                os.dup2(fd, 0)
                os.dup2(fd, 1)
                os.dup2(fd, 2)
                os.close(fd)
                # Create new process group
                os.setsid()

                os.chdir('/')
                function(*args, **kw)
            except Exception:
                try:
                    ei = sys.exc_info()
                    self.log_error('Daemonized process exception',
                                   exc_info = ei)
                finally:
                    os._exit(1)
        finally:
            os._exit(0)

class UpdateJob(BaseJob):
    storagePath = installation_service.UpdateSet.storagePath
    factory = stored_objects.ConcreteUpdateJobFactory

    def startUpdateCheck(self):
        job = self.concreteJob
        job.state = "Starting"

        self.background_run(self.updateCheck)

    def updateCheck(self):
        job = self.concreteJob
        job.pid = os.getpid()
        job.state = "Running"

        try:
            instserv = installation_service.InstallationService()
            instserv.updateAllCheck()
        except Exception:
            job.content = traceback.format_exc()
            job.state = "Exception"
        else:
            job.state = "Completed"

    def startApplyUpdate(self, instanceId):
        job = self.concreteJob
        job.state = "Starting"

        self.background_run(self.applyUpdate, instanceId)

    def applyUpdate(self, instanceId):
        job = self.concreteJob
        job.pid = os.getpid()
        job.state = "Running"

        try:
            instserv = installation_service.InstallationService()
            instserv.updateAllApply(instanceId)
        except Exception:
            job.content = traceback.format_exc()
            job.state = "Exception"
        else:
            job.state = "Completed"

    def startUpdateOperation(self, sources, flags):
        job = self.concreteJob
        job.state = "Starting"

        self.background_run(self.updateOperation, sources, flags)

    def updateOperation(self, sources, flags):
        job = self.concreteJob
        job.pid = os.getpid()
        job.state = "Running"
        try:
            instserv = installation_service.InstallationService()
            job.content = instserv.updateOperation(job, sources, flags)
        except Exception:
            job.content = traceback.format_exc()
            job.state = "Exception"
        else:
            job.state = "Completed"

class SurveyJob(BaseJob):
    storagePath = installation_service.UpdateSet.storagePath
    factory = stored_objects.ConcreteSurveyJobFactory

    def startScan(self):
        job = self.concreteJob
        job.state = "Starting"

        self.background_run(self.scan)

    def scan(self, desiredTopLevelItems):
        self.new()
        job = self.concreteJob
        job.pid = os.getpid()
        job.state = "Running"

        try:
            surveyserv = surveys.SurveyService()
            surveyserv.scan(job, desiredTopLevelItems)
        except Exception:
            job.content = traceback.format_exc()
            job.state = "Exception"
        else:
            job.state = "Completed"
        return self

class AnyJob(object):
    # XXX Make this more extensible
    _allClasses = [ UpdateJob, SurveyJob, ]

    @classmethod
    def list(cls):
        return itertools.chain(*(cls().list() for cls in cls._allClasses))

    @classmethod
    def load(self, keyId):
        for cls in self._allClasses:
            if keyId.startswith(cls.factory.factory.keyPrefix + '/'):
                return cls().load(keyId)
        return None

def startUpdateOperation(sources, flags):
    concreteJob = UpdateJob().new()
    concreteJob.startUpdateOperation(sources, flags)
    return concreteJob

def main():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--test", action="store_true", dest="test")
    parser.add_option("-m", "--mode", action="store", type="choice",
        choices=["update", "updateall", "migrate", "sync"], dest="mode")
    parser.add_option("-p", "--package", action="append", dest="package")
    (options, args) = parser.parse_args()

    kwargs = {}

    if not options.mode:
        sys.exit(-1)

    if not options.package:
        sys.exit(-1)

    kwargs[options.mode] = True
    kwargs['test'] = bool(options.test)
    
    flags = installation_service.UpdateFlags(**kwargs)
    sources = options.package
    
    concreteJob = startUpdateOperation(sources, flags)
    print concreteJob.get_job_id()
    sys.exit()

if __name__ == "__main__":
    main()
