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


import pywbem

class MixInComputerSystem(object):
    """Mixin for ComputerSystem"""

    def getComputerSystemInstance(self, env):
        # Get the local system name
        systemCreationClassName = 'CIM_ComputerSystem'
        ch = env.get_cimom_handle()
        try:
            instNames = list(ch.EnumerateInstanceNames(
                                        'root/cimv2', systemCreationClassName))
        except pywbem.CIMError:
            return None

        if not instNames:
            return None
        return instNames[0]

    def getComputerSystemName(self, env):
        # Get the local system name
        systemInstance = self.getComputerSystemInstance(env)
        if systemInstance is None:
            systemName = "localhost"
            systemCreationClassName = 'CIM_ComputerSystem'
        else:
            systemName = systemInstance['Name']
            systemCreationClassName = systemInstance.classname
        return systemCreationClassName, systemName
