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


from testutils import mock

from rpath_tools.client import hardware

from rpath_toolstest.clienttest import RpathToolsTest


class HardwareTest(RpathToolsTest):

    def setUp(self):
        RpathToolsTest.setUp(self)

    def tearDown(self):
        RpathToolsTest.tearDown(self)
        mock.unmockAll()

    def testHardwareData(self):

        class HD(hardware.HardwareData):
            def populate(slf):
                slf.data = dict(Linux_IPProtocolEndpoint = dict(
                    a = dict(IPv4Address = '1.2.3.4',
                             SubnetMask = '255.255.255.0',
                             Name = 'IP_eth0',),
                    ),
                )

        hd = HD(self.cfg)
        ret = hd.getIpAddresses()
        self.failUnlessEqual(
            [ sorted((sn, getattr(x, sn)) for sn in x.__slots__) for x in ret ],
            [
                [('device', 'eth0'), ('dns_name', '1.2.3.4'),
                 ('ipv4', '1.2.3.4'), ('ipv6', None),
                 ('netmask', '255.255.255.0')],
            ])
