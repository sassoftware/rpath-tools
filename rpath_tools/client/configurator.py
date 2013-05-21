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


import logging
import sys

from rpath_tools.client import config

from lxml import etree
from rpath_tools.client.sysdisco.configurators import RunConfigurators
from rpath_tools.client.register import LocalUuid
from rpath_tools.client.register import GeneratedUuid


logger = logging.getLogger(__name__)

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
