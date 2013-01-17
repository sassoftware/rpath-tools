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


"Simple module for generating x509 certificates"

import os
import subprocess
from conary.lib import digestlib
import gencert

class X509(object):
    class Subject(gencert.X509.X509_Name):
        __slots__ = ['C', 'ST', 'L', 'O', 'OU', 'CN', 'emailAddress']
        def __init__(self, **kwargs):
            gencert.X509.X509_Name.__init__(self)
            for slot in self.__slots__:
                val = kwargs.get(slot, None)
                if val is not None:
                    setattr(self, slot, val)

    KEY_LENGTH = 2048
    # Expire after 10 years
    EXPIRY = 3653
    TIMESTAMP_OFFSET = 0
    opensslBin = "/usr/bin/openssl"

    def __init__(self, x509, pkey):
        self.x509 = x509
        self.pkey = pkey
        self._hash_subject = None
        self._hash_issuer = None

    @classmethod
    def new(cls, subject=None, keyLength=None, serial=None, expiry=None,
            timestampOffset=None, issuer_x509=None, issuer_pkey=None,
            isCA=False):
        keyLength = (keyLength is not None and keyLength) or cls.KEY_LENGTH
        expiry = (expiry is not None and expiry) or cls.EXPIRY
        timestampOffset = (timestampOffset is not None and timestampOffset) \
            or cls.TIMESTAMP_OFFSET

        if subject is None:
            subject = cls.Subject(CN="Test Certificate")

        issuer_subject = None
        if issuer_x509 is not None:
            issuer_subject = issuer_x509.get_subject()

        rsa, x509 = gencert.new_cert(keyLength, subject, expiry,
                issuer=issuer_subject, issuer_evp=issuer_pkey, isCA=isCA,
                serial=serial, timestamp_offset=timestampOffset)

        return cls(x509, rsa)

    def load_x509_file(self, certFile):
        self.x509 = gencert.X509.load_cert(certFile)

    def load_x509(self, pem):
        self.x509 = gencert.X509.load_cert_string(pem.encode('ascii'))

    def load_pkey_file(self, keyFile, callback=None):
        kwargs = {}
        if callback is not None:
            kwargs['callback'] = callback
        self.pkey = gencert.EVP.load_key(keyFile, **kwargs)

    def load_pkey(self, pem, callback=None):
        kwargs = {}
        if callback is not None:
            kwargs['callback'] = callback
        self.pkey = gencert.EVP.load_key_string(pem.encode('ascii'), **kwargs)

    def load_from_strings(self, pemX509, pemPkey=None, callback=None):
        self.load_x509(pemX509)
        if pemPkey:
            self.load_pkey(pemPkey, callback=callback)

    @property
    def hash_issuer(self):
        if self._hash_issuer is not None:
            return self._hash_issuer
        self._hash_issuer = self.callOpenssl('issuer_hash')
        if self._hash_issuer is not None:
            return self._hash_issuer
        # Fall back to m2crypto
        self._hash_issuer = "%08x" % self.x509.get_issuer().as_hash()
        return self._hash_issuer

    @property
    def hash(self):
        if self._hash_subject is not None:
            return self._hash_subject
        self._hash_subject = self.callOpenssl('subject_hash')
        if self._hash_subject is not None:
            return self._hash_subject
        # Fall back to m2crypto
        self._hash_subject = "%08x" % self.x509.get_subject().as_hash()
        return self._hash_subject

    @property
    def fingerprint(self):
        return digestlib.sha1(self.x509.as_der()).hexdigest()

    def callOpenssl(self, option):
        if not os.path.exists(self.opensslBin):
            return None
        cmd = [ self.opensslBin, 'x509', '-noout', '-%s' % option ]
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(self.x509.as_pem())
        return stdout.strip()
