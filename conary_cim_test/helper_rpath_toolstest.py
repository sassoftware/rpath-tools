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

import helper_rpath_tools

import testbase

class HelperRpathToolsTest(testbase.TestCase):
    def testSetManagementNodes(self):
        configFilePath = self.setUpRpathToolsConfig()
        configD = configFilePath + ".d"

        try:
            registration = helper_rpath_tools.Registration(configFile=configFilePath)
            registration.setManagementNodes(["a", "b"])
            registration.setRequiredNetwork("1.1.1.1")
            configFile = os.path.join(configD, "requiredNetwork")
            self.failUnlessEqual(file(configFile).read(),
                "requiredNetwork 1.1.1.1\n")
            registration.setRequiredNetwork(None)
            self.failIf(os.path.exists(configFile))
        finally:
            pass
        configFile = os.path.join(configD, "directMethod")
        self.failUnlessEqual(file(configFile).read(), """\
directMethod []
directMethod a
directMethod b
""")
