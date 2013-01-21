#!/usr/bin/python2.4
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
import subprocess

from conary.lib import util

class ConfigManager(object):
    ConfigFilePath = "/var/lib/rpath-tools/values.xml"
    BinaryPath = "/usr/bin/rpath-configurator"

    class Configuration(object):
        __slots__ = [ 'path' ]

        def __init__(self, **kwargs):
            for slot in self.__slots__:
                setattr(self, slot, kwargs.get(slot))

        def _getValue(self):
            if os.path.exists(self.path):
                return file(self.path).read()
            return None

        def _setValue(self, value):
            ConfigManager.logger.log_info("Setting value for %s" % self.path)
            util.mkdirChain(os.path.dirname(self.path))
            f = util.AtomicFile(self.path, chmod=0600)
            f.write(value)
            f.commit()

        value = property(_getValue, _setValue)

    def __init__(self, logger):
        self.__class__.logger = logger

    def iterConfigurations(self):
        config = self.Configuration(path=self.ConfigFilePath)
        yield config

    def getConfiguration(self, path):
        if path != self.ConfigFilePath:
            raise Exception("No implementation for path %s" % (path, ))
        return self.Configuration(path=path)

    def test(self, configuration):
        self.logger.log_info("Testing configuration from %s" % configuration.path)

    def apply(self, configuration):
        self.logger.log_info("Applying configuration from %s" % configuration.path)
        return self._apply(configuration)

    def _apply(self, configuration):
        cmd = [ self.BinaryPath, 'write' ] # removed configuration.path
        try:
            p = subprocess.Popen(cmd, shell=False, stdin=None,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            retcode = p.returncode
        except OSError, e:
            retcode, stdout, stderr = 1024, "", str(e)
        if retcode != 0:
            ConfigManager.logger.log_error(
                "Error running command '%s': %s; %s" % (
                    " ".join(cmd), stdout, stderr))

        return retcode, stdout, stderr
