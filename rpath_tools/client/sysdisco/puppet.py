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


import os


# rpath-tools does not require Puppet but can trigger it conditions are right
# rpath_site.pp is generated by tag handlers when puppet content is packaged
# containing the concatenation of /etc/puppet/modules/*/rpath/*



PUPPET_BIN  = "/usr/bin/puppet"
PUPPET_SITE = "/etc/puppet/manifests/rpath_site.pp"
PUPPET_LOG  = "/var/log/rpath_puppet.log"


class Puppet(object):

    def _read(self, filename):
        return open(filename).read()


    def puppetApply(self, logger):

        # kick off a puppet run at the end of an rpath-configurator write 
        # if puppet is present
        # and tag handlers have generated an rpath_site.pp

        if not os.path.isfile(PUPPET_BIN):
            return 0
        if not os.path.isfile(PUPPET_SITE):
            # no rpath puppet stuff to do
            return 0

        cmd = "%s apply %s --color=false >%s 2>&1" % (PUPPET_BIN,
                                            PUPPET_SITE, PUPPET_LOG)
        logger.normal(cmd)
        rc = os.system(cmd)
        if rc != 0:
            logger.error("puppet apply failed")
        return rc

    def run(self, logger):
        # run supported/integrated configuration management systems
        pc = self.puppetApply(logger)
        # copy puppet data into iconfig log for this run
        if os.path.exists('/var/log/rpath_puppet.log'):
            logFile = file('/var/log/rpath_tools.log', 'a')
            logData2 = file('/var/log/rpath_puppet.log').read()
            logFile.write(logData2)
            logFile.close()
            # allow puppet data from run to be seen from CIM
            print logData2

        return pc

if __name__ == '__main__':
    import sys
    from conary.lib import util
    sys.excepthook = util.genExcepthook()
    ruppet = Puppet()
    import logging
    logger = logging.getLogger('client')
    pc = ruppet.run(logger)
    print pc
