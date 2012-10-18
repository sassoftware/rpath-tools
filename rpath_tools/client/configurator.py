#
# Copyright (c) rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#


import logging
import sys

from rpath_tools.client import config

from lxml import etree
from rpath_tools.client.sysdisco.configurators import RunConfigurators
from rpath_tools.client.register import LocalUuid
from rpath_tools.client.register import GeneratedUuid


logger = logging.getLogger('client')

def main(cfg=None, configurators=None):
    if not cfg:
        cfg = config.RpathToolsConfiguration()
        cfg.topDir = '/etc/conary'
    r = Configurator(cfg, configurators)
    result = r.run()
    return result


class Configurator(object):

    def __init__(self, cfg, configurators):
        self.cfg = cfg
        self.configurators = configurators
        self.generatedUuid = GeneratedUuid().uuid
        self.localUuidObj = LocalUuid(self.cfg.localUuidFilePath,
                                 self.cfg.localUuidOldDirectoryPath,
                                 deviceName=None)

    def _execute(self):
        c = RunConfigurators(self.configurators)
        root = c.toxml()
        return root


    def run(self):
        logger.info('Attempting to run configurators on %s' % self.localUuidObj.uuid)
        configurated = self._execute()
        if len(configurated):
            logger.info('Configurators succeeded')
            print etree.tostring(configurated)
            return True
        logger.error("Configuration failed")
        return False


if __name__ == '__main__':
    sys.exit(main())
