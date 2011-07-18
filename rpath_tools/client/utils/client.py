#
# Copyright (c) 2010 rPath, Inc.
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
