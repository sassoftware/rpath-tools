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


import httplib
import urllib2
import socket
from M2Crypto import SSL


class HTTPSConnection(httplib.HTTPConnection):
    """
    httplib connection that checks SSL peer certificates but doesn't check
    commonName.
    """

    default_port = httplib.HTTPS_PORT
    socketFactory = SSL.Connection

    def __init__(self, host, port=None, strict=None, ssl_context=None):
        httplib.HTTPConnection.__init__(self, host, port, strict)
        if not ssl_context:
            ssl_context = SSL.Context('sslv23')
        self.ssl_ctx = ssl_context

    def connect(self):
        self.sock = self.socketFactory(self.ssl_ctx)
        self.sock.clientPostConnectionCheck = self.checkSSL
        self.sock.connect((self.host, self.port))

    def close(self):
        # See M2Crypto/httpslib.py:67
        pass

    def checkSSL(self, cert, host):
        """Just make sure a cert was provided.

        commonName is deliberately not checked since we were probably given an
        IP only.
        """
        return cert is not None


class HTTPSHandler(urllib2.AbstractHTTPHandler):
    """
    urllib2 HTTPS handler that checks SSL peer certificates but doesn't check
    commonName.
    """

    connectionFactory = HTTPSConnection
    https_request = urllib2.AbstractHTTPHandler.do_request_

    def __init__(self, ssl_context=None):
        urllib2.AbstractHTTPHandler.__init__(self)
        self.ssl_context = ssl_context

    def https_open(self, req):
        host = req.get_host()
        if not host:
            raise urllib2.URLError('no host given')

        # Begin change from urllib2
        h = self.connectionFactory(host=host, ssl_context=self.ssl_context)
        # End change from urllib2

        h.set_debuglevel(self._debuglevel)

        headers = dict(req.headers)
        headers.update(req.unredirected_hdrs)
        # We want to make an HTTP/1.1 request, but the addinfourl
        # class isn't prepared to deal with a persistent connection.
        # It will try to read all remaining data from the socket,
        # which will block while the server waits for the next request.
        # So make sure the connection gets closed after the (only)
        # request.
        headers["Connection"] = "close"
        try:
            h.request(req.get_method(), req.get_full_url(), req.data, headers)
            r = h.getresponse()
        except socket.error, err: # XXX what error?
            raise urllib2.URLError(err)

        # Pick apart the HTTPResponse object to get the addinfourl
        # object initialized properly.

        # Wrap the HTTPResponse object in socket's file object adapter
        # for Windows.  That adapter calls recv(), so delegate recv()
        # to read().  This weird wrapping allows the returned object to
        # have readline() and readlines() methods.

        # XXX It might be better to extract the read buffering code
        # out of socket._fileobject() and into a base class.

        r.recv = r.read
        fp = socket._fileobject(r)

        resp = urllib2.addinfourl(fp, r.msg, req.get_full_url())
        resp.code = r.status
        resp.msg = r.reason
        return resp
