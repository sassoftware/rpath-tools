#!/usr/bin/python

from xml.etree import cElementTree as etree

from conary import conarycfg
from conary import conaryclient
from rpath_tools.client.utils.config_descriptor_cache import ConfigDescriptorCache

class Descriptors(object):
    def __init__(self):
        self.cfg = conarycfg.ConaryConfiguration(True)
        self.client = conaryclient.ConaryClient(self.cfg)

    def gather(self):
        group = [ x for x in self.client.getUpdateItemList()
                    if x[0].startswith('group-') and 
                    x[0].endswith('-appliance') ][0]

        desc = ConfigDescriptorCache(self.client.getDatabase()).getDescriptor(group)
        if desc:
            desc.setDisplayName('ConfigurationDescriptor')
            desc.addDescription('ConfigurationDescriptor')
        return desc

    def toxml(self, validate=False):
        desc = self.gather()
        if desc:
            return  desc.toxml(validate=validate)
        return desc

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()

    descriptors = Descriptors()
    xml = etree.fromstring(descriptors.toxml())
    print etree.tostring(xml)

