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
import urllib2
import urlparse

logger = logging.getLogger('client')

class Client(object):
    def __init__(self, url):
        self.url = url

    def request(self, data=None):
        logger.debug("Sending XML data as POST:\n%s" % data)
        self.response = urllib2.urlopen(self.url, data=data)
        self.responseBody = self.response.read()
        if self.response.code in self.SUCCESS_CODES:
            return True
        else:
            return False

class RegistrationClient(Client):

    SUCCESS_CODES = [200, 201]
    PATH = '/api/inventory/systems/'
    SCHEME = 'https'

    def __init__(self, url):
        self.url = urlparse.urlunsplit([self.SCHEME, url, self.PATH, None, None])

    def register(self, data):
        registered = self.request(data)

        if not registered:
            logger.error("Failed registration with %s." % self.url)
            logger.error("Response code: %s" % self.response.code)
            logger.error("Response: %s" % self.responseBody)

        return registered
