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



from rpath_tools.client import updater

import logging

logger = logging.getLogger(name='__name__')



class Preview(object):

    def __init__(self, sources=None):
        self.sources = sources

    def preview(self, sources):
        '''
        @param sources: should be a string representing the desired
                        system-model for the system. For classic update
                        path sources should be a string of the top level item

        @type sources : string
        '''

        return updater.preview(sources, preview=True)


if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    sources = [ 'group-smitty-c6e-goad-appliance=/smitty-c6e-goad.eng.rpath.com@rpath:smitty-c6e-goad-1-devel/1-63-1' ]
    preview = Preview()
    xml = preview.preview(sources)
    print xml
