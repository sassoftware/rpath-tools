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


# test that we can use API finder to find the endpoint of a service regardless of a particular version
# right now apifinder is used for both rpath-tools and rbuild (which has a copy of it, for lack
# of a common module shared between the two that would be a good place to hold it). 

import os
import sys
import time
import StringIO

from testutils import mock
from rpath_tools.client.utils.apifinder import ApiFinder
from rpath_toolstest.clienttest import testsetup
from rpath_toolstest.clienttest import RpathToolsTest

from rpath_models import System

# The following API example was sampled from real instances running the respective
# rBuilder versions:

EDGE_SLASH_API = """<api><api_versions><api_version id="https://rbanext-eng.eng.rpath.com/api/v1" description="rBuilder REST API version 1" name="v1"/></api_versions></api>
"""

EDGE_SLASH_API_SLASH_V1 = """<!--Methods:
    GET:
        Authentication: none
    POST:
        not supported
    PUT:
        not supported
    DELETE:
        not supported--><api_version id="http://rbalast.eng.rpath.com/api/v1" name="v1" description="rBuilder REST API version 1"><changelogs id="http://rbalast.eng.rpath.com/api/v1/changelogs"/><module_hooks id="http://rbalast.eng.rpath.com/api/v1/module_hooks"/><jobs id="http://rbalast.eng.rpath.com/api/v1/jobs"/><users id="http://rbalast.eng.rpath.com/api/v1/users"/><roles id="http://rbalast.eng.rpath.com/api/v1/rbac/roles"/><version_info><rbuilder_version>6.0.0</rbuilder_version><rmake_version>9fdc6b93d541</rmake_version><conary_version>6699456fc08f</conary_version><product_definition_schema_version>4.3</product_definition_schema_version></version_info><grants id="http://rbalast.eng.rpath.com/api/v1/rbac/grants"/><project_branch_stages id="http://rbalast.eng.rpath.com/api/v1/project_branch_stages"/><inventory id="http://rbalast.eng.rpath.com/api/v1/inventory"/><reports id="http://rbalast.eng.rpath.com/api/v1/reports"/><rbac id="http://rbalast.eng.rpath.com/api/v1/rbac"/><platforms id="http://rbalast.eng.rpath.com/api/platforms"/><project_branches id="http://rbalast.eng.rpath.com/api/v1/project_branches"/><session id="http://rbalast.eng.rpath.com/api/v1/session"/><products id="http://rbalast.eng.rpath.com/api/products"/><projects id="http://rbalast.eng.rpath.com/api/v1/projects"/><config_info><is_external_rba>false</is_external_rba><image_import_enabled>true</image_import_enabled><maintenance_mode>false</maintenance_mode><hostname>rbalast.eng.rpath.com</hostname><rbuilder_id>rpathdev</rbuilder_id><account_creation_requires_admin>false</account_creation_requires_admin><inventory_configuration_enabled>true</inventory_configuration_enabled></config_info><notices id="http://rbalast.eng.rpath.com/api/v1/notices"/><packages id="http://rbalast.eng.rpath.com/api/v1/packages"/><query_sets id="http://rbalast.eng.rpath.com/api/v1/query_sets"/><permissions id="http://rbalast.eng.rpath.com/api/v1/rbac/permissions"/></api_version>
"""

DIRK_SLASH_API = """<?xml version='1.0' encoding='UTF-8'?>
<rbuilderStatus id="http://qa4.eng.rpath.com/api">
  <version>6.0.4</version>
  <conaryVersion>4afddc5fcf21</conaryVersion>
  <rmakeVersion>9fdc6b93d541</rmakeVersion>
  <userName>anonymous</userName>
  <hostName>qa4.eng.rpath.com</hostName>
  <isRBO>false</isRBO>
  <isExternalRba>false</isExternalRba>
  <accountCreationRequiresAdmin>false</accountCreationRequiresAdmin>
  <identity>
    <rbuilderId>rpathdev</rbuilderId>
    <serviceLevel status="Full" daysRemaining="-1" expired="false" limited="false"/>
    <registered>true</registered>
  </identity>
  <products href="http://qa4.eng.rpath.com/api/products/"/>
  <users href="http://qa4.eng.rpath.com/api/users/"/>
  <platforms href="http://qa4.eng.rpath.com/api/platforms/"/>
  <registration href="http://qa4.eng.rpath.com/api/registration"/>
  <reports href="http://qa4.eng.rpath.com/api/reports/"/>
  <inventory href="http://qa4.eng.rpath.com/api/inventory/"/>
  <query_sets href="http://qa4.eng.rpath.com/api/query_sets/"/>
  <packages href="http://qa4.eng.rpath.com/api/packages/"/>
  <moduleHooks href="http://qa4.eng.rpath.com/api/moduleHooks/"/>
  <maintMode>false</maintMode>
  <proddefSchemaVersion>4.2</proddefSchemaVersion>
  <inventoryConfigurationEnabled>true</inventoryConfigurationEnabled>
  <imageImportEnabled>true</imageImportEnabled>
</rbuilderStatus>
"""

CLAYMORE_SLASH_API = """<?xml version='1.0' encoding='UTF-8'?>
<rbuilderStatus id="http://dhcp29.eng.rpath.com/api">
  <version>5.8.10</version>
  <conaryVersion>4afddc5fcf21</conaryVersion>
  <rmakeVersion>af51871ceea9</rmakeVersion>
  <userName>anonymous</userName>
  <hostName>dhcp29.eng.rpath.com</hostName>
  <isRBO>false</isRBO>
  <isExternalRba>false</isExternalRba>
  <accountCreationRequiresAdmin>false</accountCreationRequiresAdmin>
  <identity>
    <rbuilderId>rpathdev</rbuilderId>
    <serviceLevel status="Full" daysRemaining="-1" expired="false" limited="false"/>
    <registered>true</registered>
  </identity>
  <products href="http://dhcp29.eng.rpath.com/api/products/"/>
  <users href="http://dhcp29.eng.rpath.com/api/users/"/>
  <platforms href="http://dhcp29.eng.rpath.com/api/platforms/"/>
  <registration href="http://dhcp29.eng.rpath.com/api/registration"/>
  <reports href="http://dhcp29.eng.rpath.com/api/reports/"/>
  <inventory href="http://dhcp29.eng.rpath.com/api/inventory/"/>
  <moduleHooks href="http://dhcp29.eng.rpath.com/api/moduleHooks/"/>
  <maintMode>false</maintMode>
  <proddefSchemaVersion>4.2</proddefSchemaVersion>
  <inventoryConfigurationEnabled>true</inventoryConfigurationEnabled>
  <imageImportEnabled>true</imageImportEnabled>
</rbuilderStatus>
"""

class MockApiFinder(ApiFinder):

    def __init__(self, simulate_version):
        self.simulate_version = simulate_version
        ApiFinder.__init__(self, 'doesnotexist.example.com')

    def _read(self, url):
        ''' 
        read method mocked so HTTP requests are returned as if they came
        from a particular version of rbuilder
        '''
        if self.simulate_version == 'dirk':
             if url.endswith('/api'):
                return DIRK_SLASH_API
        elif self.simulate_version == 'claymore':
             if url.endswith('/api'):
                return CLAYMORE_SLASH_API
        elif self.simulate_version == 'edge':
             if url.endswith('/api'):
                return EDGE_SLASH_API
             if url.endswith('/api/v1'):
                return EDGE_SLASH_API_SLASH_V1
        raise Exception("unmocked URL or simulation version: %s, %s" % (simulate_version, url))

class RegistrationTest(RpathToolsTest):

    def setUp(self):
        RpathToolsTest.setUp(self)

    def tearDown(self):
        RpathToolsTest.tearDown(self)
        mock.unmockAll()

    def testClaymore(self):
        mf = MockApiFinder('claymore')
        result = mf.url('inventory')
        self.assertEquals(result.version, 0)
        self.assertEquals(result.url, 'http://dhcp29.eng.rpath.com/api/inventory/')

    def testDirk(self):
        mf = MockApiFinder('dirk')
        result = mf.url('inventory')
        self.assertEquals(result.version, 0)
        self.assertEquals(result.url, 'http://qa4.eng.rpath.com/api/inventory/')

    def testEdge(self):
        mf = MockApiFinder('edge')
        result = mf.url('inventory')
        self.assertEquals(result.version, 1)
        self.assertEquals(result.url, 'http://rbalast.eng.rpath.com/api/v1/inventory')
