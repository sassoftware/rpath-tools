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
import sys


curDir = os.path.dirname(__file__)
for dirlevel in range(10):
    testsuitePath = os.path.realpath(curDir + '/..' * dirlevel)
    if os.path.exists(testsuitePath + '/testsuite.py'):
        break
else:
    raise RuntimeError('Could not find testsuite.py!')
if not testsuitePath in sys.path:
    sys.path.insert(0, testsuitePath)


import testsuite
testsuite.setup()


def main():
    if sys._getframe(1).f_globals['__name__'] == '__main__':
        testsuite.main()
