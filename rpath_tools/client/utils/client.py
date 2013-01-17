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
from M2Crypto import SSL
import urllib2
import urlparse

import rpath_models
from rpath_tools.client.utils.apifinder import ApiFinder
from rpath_tools.client.errors import RpathToolsRegistrationError
from rpath_tools.client.utils import httpslib

logger = logging.getLogger('client')

class Client(object):
    def __init__(self, url, ssl_context=None):
        self.url = url
        self.opener = urllib2.OpenerDirector()
        if ssl_context is None:
            ssl_context = SSL.Context()
        self.opener.add_handler(httpslib.HTTPSHandler(ssl_context))
        self.opener.add_handler(urllib2.HTTPHandler())

    def request(self, data=None):
        logger.debug("Sending XML data as POST:\n%s" % data)
        try:
            self.response = self.opener.open(self.url, data=data)
        except urllib2.URLError, e:
            raise RpathToolsRegistrationError(e.reason)
        except SSL.SSLError, e:
            raise RpathToolsRegistrationError(
                "SSL error while connecting to %s: %s" % (self.url, str(e)))
        return self.response.code in self.SUCCESS_CODES

class RegistrationClient(Client):

    SUCCESS_CODES = [200, 201]

    # refuse to work with servers newer than this
    # but try older versions if that's all we have
    # API call is supported to the dawn of versioned time
    API_MIN_VERSION = 0 
    API_MAX_VERSION = 1

    def __init__(self, server, ssl_context=None):
        Client.__init__(self, server, ssl_context=ssl_context)
        self.finder = ApiFinder(
            server,
            minVersion=RegistrationClient.API_MIN_VERSION,
            maxVersion=RegistrationClient.API_MAX_VERSION,
            opener=self.opener,
            secure=True
        )
        match = self.finder.url('inventory')
        if match.url.endswith("/"):
            self.url = "%ssystems/" % match.url
        else:
            self.url = "%s/systems/" % match.url

    def register(self, data):
        registered = self.request(data)

        if not registered:
            logger.error("Failed registration with %s." % self.url)
            logger.error("Response code: %s" % self.response.code)
            logger.error("Response: %s" % self.response.read())
            self.system = None
        else:
            self.system = rpath_models.System()
            self.system.parseStream(self.response)

        return registered
