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


import urllib
import urllib2
import urlparse

class Client(object):
    def __init__(self, url):
        self.url = url

    def request(self, data=None):
        print data
        return
        self.response = urllib.urlopen(self.url, data)
        self.responseBody = self.response.read()
        return self.responseBody

class ActivationClient(Client):
    def activate(self, data):
        print data
        # return None
        return data
        return self.request(data)
