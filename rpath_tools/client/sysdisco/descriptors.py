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


from lxml import etree

from conary import conarycfg
from conary import conaryclient
from rpath_tools.client.utils.config_descriptor_cache import ConfigDescriptorCache

class Descriptors(object):
    def __init__(self):
        self.cfg = conarycfg.ConaryConfiguration(True)
        self.client = conaryclient.ConaryClient(self.cfg)

    def gather(self):
        desc = None
        groups = [ x for x in self.client.getUpdateItemList()
                    if x[0].startswith('group-') and
                    x[0].endswith('-appliance') ]
        if len(groups):
            group = groups[0]
            desc = ConfigDescriptorCache(self.client.getDatabase()).getDescriptor(group)
        if desc:
            desc.setDisplayName('ConfigurationDescriptor')
            desc.addDescription('ConfigurationDescriptor')
        return desc

    def toxml(self, validate=False):
        desc = self.gather()
        if desc:
            return desc.toxml(validate=validate)
        return desc

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

    descriptors = Descriptors()
    xml = etree.fromstring(descriptors.toxml())
    print etree.tostring(xml)
