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


from conary.lib import util

from rpath_tools.lib import clientfactory
from rpath_tools.lib import concrete_job

import logging

logger = logging.getLogger(name = '__name__')



class SystemModelServiceError(Exception):
    "Base class"

class NoUpdatesFound(SystemModelServiceError):
    "Raised when no updates are available"

class RepositoryError(SystemModelServiceError):
    "Raised when a repository error is caught"


class Updater(object):

    conaryClientFactory = clientfactory.ConaryClientFactory

    def __init__(self, systemModel=None):
        self.contents = systemModel


    def debug(self, sources, flags):
        fname = "/tmp/system-model.preview"
        file(fname, "w").write(sources)
        concreteJob = concrete_job.UpdateJob.previewSyncOperation(fname, flags)
        xml = concreteJob.contents
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

    operation = Updater(blob)
    operation.debug()
