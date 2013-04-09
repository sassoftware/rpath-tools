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



from rpath_tools.lib import clientfactory
from rpath_tools.lib import concrete_job
from rpath_tools.lib import installation_service

import logging

logger = logging.getLogger(name='__name__')



class Preview(object):
    conaryClientFactory = clientfactory.ConaryClientFactory

    def __init__(self, cclient=None):
        self.cclient = cclient

    def _getClient(self, force=False):
        if self.cclient is None or force:
            self.cclient = self.conaryClientFactory().getClient()
        return self.cclient

    conaryClient = property(_getClient)

    def previewUpdateOperation(self, sources, flags, callback=None):
        '''Use updateOperation to create a preview by setting flag.test'''
        # FIXME XXX
        # Create a job to pass to installation_service
        job = None
        op = installation_service.InstallationService()
        xml = op.updateOperation(job, sources, flags)
        return xml


    def preview(self, sources):
        flags = installation_service.UpdateFlags(migrate=True,test=True)
        if self.is_system_model:
            fname = "/tmp/system-model.preview"
            file(fname, "w").write(sources)
            concreteJob = concrete_job.UpdateJob.previewSyncOperation(fname, flags)
            xml = concreteJob.contents
        else:
            xml = self.previewUpdateOperation(sources, flags)
        if xml:
            return xml
        return '<preview/>'

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    sources = [ 'group-smitty-c6e-goad-appliance=/smitty-c6e-goad.eng.rpath.com@rpath:smitty-c6e-goad-1-devel/1-63-1' ]
    preview = Preview()
    xml = preview.preview(sources)
    print xml
