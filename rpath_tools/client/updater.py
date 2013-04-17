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


from conary.lib import util


from rpath_tools.lib import update
from rpath_tools.lib import jobs
from rpath_tools.lib import errors
from rpath_tools.lib import installation_service

import tempfile
import os

import logging

logger = logging.getLogger(__name__)


class Updater(update.UpdateService):

    def __init__(self, value=None):
        super(Updater, self).__init__()
        self.systemModelPath = self.conaryCfg.modelPath
        self.tmpDir = self.conaryCfg.tmpDir

    @property
    def is_system_model(self):
        return self._system_model_exists()

    def storeTempSystemModel(self, data):
        fd, path = tempfile.mkstemp(prefix='system-model.', dir=self.tmpDir)
        try:
            f = os.fdopen(fd, 'w')
            f.write(str(str(data)))
        except Exception, e:
            #FIXME
            raise Exception, str(e)
        return path

    def updateOperation(self, sources, preview=True):
        '''
        system-model sources must be a string representation of
        the system-model file
        classic method sources is a list of top level items
        '''
        xml = '<preview/>'
        if self.is_system_model:
            if not sources:
                sources = file(self.systemModelPath).read()
            tempSystemModelPath = self.storeTempSystemModel(sources)
            task = jobs.SyncPreviewTask().new()
            # Currently we have to call the steps manually
            # to avoid a double fork
            task.preFork(tempSystemModelPath)
            task.run(tempSystemModelPath)
            xml = task.job.content
        else:
            # WARNING if preview is set to False the update will be applied
            flags = installation_service.InstallationService.UpdateFlags(
                                migrate=True, test=preview)
            task = jobs.startUpdateOperation(sources=sources, flags=flags)
            task()
            xml = task.xml()
        return xml


    def applyOperation(self, jobid):
        xml = '<preview/>'
        if self.is_system_model:
            task = jobs.SyncApplyTask().load(jobid)
            # Currently we have to call the steps manually
            # to avoid a double fork
            task.preFork()
            task.run()
            xml = task.job.content
        else:
            logger.error('Classic systems do not'
                ' freeze jobs so we can not apply a frozen job')
            raise errors.NotImplementedError
        return xml

    def preview(self, sources):
        # Stub for preview operation
        preview_xml = self.updateOperation(sources)

        # jobid for apply will be in preview
        return preview_xml

    def apply(self, jobid):
        # Stub for apply operation
        apply_xml = self.applyOperation(jobid)
        return apply_xml

    def update(self, sources):
        # DEPRECATED : As I write this...
        # Used for non system-model systems
        preview_xml = self.updateOperation(sources, preview=False)
        return preview_xml

    def debug(self, sources):
        systemModelPath = '/tmp/system-model.debug'
        file(systemModelPath, "w").write(sources)
        task = jobs.SyncPreviewTask().new()
        # Currently we have to call the steps manually
        # to avoid a double fork
        task.preFork(systemModelPath)
        task.run(systemModelPath)
        xml = task.job.content
        return xml


if __name__ == '__main__':
    import sys
    sys.excepthook = util.genExcepthook()

    fileName = sys.argv[1]
    try:
        with open(fileName) as f:
            blob=f.read()
    except EnvironmentError:
        print 'oops'

