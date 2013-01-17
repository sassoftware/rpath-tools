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


import os
import time
import StringIO

from testutils import mock

from rpath_tools.client import register

from rpath_toolstest.clienttest import RpathToolsTest

from rpath_models import System

class RegistrationTest(RpathToolsTest):

    def setUp(self):
        RpathToolsTest.setUp(self)
        mock.mock(register.LocalUuid, '_getDmidecodeUuid')
        register.LocalUuid._getDmidecodeUuid._mock.setReturn('GENERATEDUUID')
        self.reg = register.Registration.registration(self.cfg)
        clientsDir = os.path.join(self.cfg.topDir, 'clients')
        cfg = self.reg.sfcbConfig
        cfg['sslClientTrustStore'] = os.path.join(self.cfg.topDir, 'clients')

    def tearDown(self):
        RpathToolsTest.tearDown(self)
        mock.unmockAll()

    def testRegistration(self):
        self.assertTrue(isinstance(self.reg, register.Registration))

    def notestReadCredentials(self):
        certPath, keyPath = self.reg.readCredentials()
        cert = open(certPath).read()
        key = open(keyPath).read()
        self.assertEquals('-----BEGIN CERTIFICATE-----', cert[0:27])
        self.assertEquals('-----BEGIN RSA PRIVATE KEY-----', key[0:31])
        
    def testUpdateRegistrationFile(self):
        mock.mock(time, 'time')
        time.time._mock.setReturn('1234567890')
        self.reg.updateRegistrationFile()
        self.assertEquals('1234567890',
            open(self.cfg.lastRegistrationFilePath).read())

    def testRegisterSystem(self):
        system = System(
            generated_uuid = 'GENERATEDUUID',
            local_uuid = 'LOCALUUID',
            ssl_client_certificate = 'SSLCLIENTCERTIFICATE',
            launch_date = '2010-09-27T14:57:16.590896+00:00',
        )
        sio = StringIO.StringIO()
        system.serialize(sio)
        systemXml = sio.getvalue()

        registerDirect = mock.MockObject()
        registerSLP = mock.MockObject()
        self.reg.registrationMethods = {'DIRECT' : registerDirect,
                                      'SLP' : registerSLP}

        # DIRECT (successful)
        success = self.discardOutput(self.reg.registerSystem, system)
        registerDirect._mock.assertCalled(systemXml)
        registerSLP._mock.assertNotCalled()
        self.assertTrue(success)
        registerDirect._mock.calls = []
        registerSLP._mock.calls = []

        # DIRECT (successful), SLP (not called)
        self.cfg.registrationMethod.append('SLP')
        success = self.discardOutput(self.reg.registerSystem, system)
        registerSLP._mock.assertNotCalled()
        self.assertTrue(success)
        registerDirect._mock.calls = []
        registerSLP._mock.calls = []

        # DIRECT (failure), SLP (successful)
        registerDirect._mock.setDefaultReturn(None)
        success = self.discardOutput(self.reg.registerSystem, system)
        registerDirect._mock.assertCalled(systemXml)
        registerSLP._mock.assertCalled(systemXml)
        self.assertTrue(success)
        registerDirect._mock.calls = []
        registerSLP._mock.calls = []

        # DIRECT (failure), SLP (failure)
        registerDirect._mock.setDefaultReturn(None)
        registerSLP._mock.setDefaultReturn(None)
        success = self.discardOutput(self.reg.registerSystem, system)
        self.assertFalse(success)

    def test_register(self):
        system = System(
            generated_uuid = 'GENERATEDUUID',
            local_uuid = 'LOCALUUID',
            ssl_client_certificate = 'SSLCLIENTCERTIFICATE',
        )

        sio = StringIO.StringIO()
        system.serialize(sio)
        systemXml = sio.getvalue()

        self.cfg.conaryProxyFilePath = \
            os.path.join(self.testPath, 'rpath-tools-conaryProxy')

        # Return a different client cert, and no client key
        # This is a self-signed cert
        system.ssl_client_certificate = certificate_selfSigned
        system.ssl_client_key = None

        remote = '1.1.1.1:443'

        regclientClass = mock.MockObject()
        regclient = mock.MockObject()
        regclientClass._mock.setDefaultReturn(regclient)

        regclient.register._mock.setReturn(True, systemXml)
        regclient._mock.set(system=system)
        self.mock(register.utils.client, 'RegistrationClient', regclientClass)

        certPath = os.path.join(self.testPath, "clients/c688bead.0")
        self.failIf(os.path.exists(certPath))
        ret = self.discardOutput(self.reg._register, remote, systemXml)
        self.failUnless(os.path.exists(certPath))
        self.failUnless(os.path.exists(os.path.join(self.testPath, 'rpath-tools-conaryProxy')))
        proxy = open(os.path.join(self.testPath, 'rpath-tools-conaryProxy'))
        self.assertEquals(proxy.read(), 'conaryProxy https://1.1.1.1\n')
        proxy.close()

        st = os.stat(certPath)

        # Running the code again should not overwrite
        ret = self.discardOutput(self.reg._register, remote, systemXml)
        st2 = os.stat(certPath)
        self.failUnlessEqual(
            (st.st_dev, st.st_ino),
            (st2.st_dev, st2.st_ino))

        # Munge cert, make sure it gets re-done
        file(certPath, "w").write("Blah!")
        ret = self.discardOutput(self.reg._register, remote, systemXml)
        self.failUnless(file(certPath).read().startswith(
            "-----BEGIN CERTIFICATE-----"))

        # Cert signed by a CA
        system.set_ssl_client_certificate(certificate_caSigned)

        # Make sure the issuer's cert goes away - create it first
        issuerCertPath = os.path.join(self.testPath, "clients/6d8bb0a1.0")
        file(issuerCertPath, "w").write("Some stuff")


        certPath = os.path.join(self.testPath, "clients/01081fc7.0")
        self.failIf(os.path.exists(certPath))
        ret = self.discardOutput(self.reg._register, remote, systemXml)
        self.failUnless(os.path.exists(certPath))
        # We don't remove the LG CA just yet, since a CIM call may be running
        #self.failIf(os.path.exists(issuerCertPath))
        self.failUnless(os.path.exists(issuerCertPath))

    def testLocalUuidForEC2(self):
        register.utils.runningInEC2 = lambda: True
        class LocalUuid(register.LocalUuid):
            @classmethod
            def _readInstanceIdFromEC2(cls):
                return "i-0123456"

        uuidFile = os.path.join(self.testPath, "local-uuid")
        self.failUnlessEqual(LocalUuid._getEC2InstanceId(), 'i-0123456')

        a = LocalUuid(uuidFile, self.testPath)
        a.read()
        self.failUnlessEqual(a.uuid, '1288b599-4d13-cbf3-8d22-100353a3453b')

        # Return None if it claims it's not on Amazon
        register.utils.runningInEC2 = lambda: False
        self.failUnlessEqual(LocalUuid._getEC2InstanceId(), None)

    def testLocalUuidGetMac(self):
        uuidFile = os.path.join(self.testPath, "local-uuid")
        a = register.LocalUuid(uuidFile, self.testPath, 'eth0')
        uuid = a._getUuidFromMac()
        # Just test that we got something back that looks like a uuid
        self.failUnlessEqual(len(uuid), 36)
        


certificate_selfSigned = """
-----BEGIN CERTIFICATE-----
MIICzjCCAbagAwIBAgICB04wDQYJKoZIhvcNAQEFBQAwITEfMB0GA1UEAxMWcmVp
bmhvbGQucmR1LnJwYXRoLmNvbTAeFw0xMDA5MDIwMTIxMDhaFw0xMDA5MDkwMTIx
MDhaMCExHzAdBgNVBAMTFnJlaW5ob2xkLnJkdS5ycGF0aC5jb20wggEiMA0GCSqG
SIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUnTxyU25q7vCXTQr6Y3DRB4bPRoTVAFKi
khDwbMXohp9grz8un3HxSyBCITwoVjctiIZNUWpyTFKWXt56XKiugYqvqE3lZGyH
HFjcLdvvIWydiw66Ruh//hCnktS1zPETTxoyhzxX0XhepSGO+383MIoRQU3ffoIf
b+K9EyRJ8WASc/h/KnVYpHWBVGa2ROAU4Ea/FzuatO3ma8Kf18PpHnylwRs/vN9y
5WcTHwhwCL+/z1m/AMrPjJ9mlqLUCkQKuZRcUk2xdBOpShxp0g5tvyReO7QCcbFZ
pHGPypuelcMxxBPi+WdFhiZMCdOHdwXLtGhsAliouOhVNEgU+/kDAgMBAAGjEDAO
MAwGA1UdEwEB/wQCMAAwDQYJKoZIhvcNAQEFBQADggEBAA02T0knSOe5Z5eAN601
+zuKrM57MHbYb7ekar7AoQ7o8lUb09oQUfSQEwzKg04y4ukaPXPDrlDWlyysUESw
oQD4xUrNzpsTKmBNj2mlnhc9TpRAUuUZNMl2Jk+4+ywcpXE//PiLUUINDtkZqa6G
MEtZ9+1BsspfvhE/BFE6Zhrus7DuEJ9GxA332Ws0WpbjGzUgEKBqHJEYlU7vr0S9
TtoFTZ60ArvHc5Nzl/dXiEpr4bRI973Y56KGkmP7yBIFQM0Ku374ARNCdp9LVIiQ
wM0ltKJP9mAzs3/ewgYgZ7pfgHqJuF/d/ChgfnUNUl9Hy6f7wKWNb2QqaGew41FN
pt8=
-----END CERTIFICATE-----
"""

certificate_caSigned = """
-----BEGIN CERTIFICATE-----
MIIDazCCAlOgAwIBAgIBADANBgkqhkiG9w0BAQUFADBhMTEwLwYDVQQKEyhyQnVp
bGRlciBMb3ctR3JhZGUgQ2VydGlmaWNhdGUgQXV0aG9yaXR5MSwwKgYDVQQLEyND
cmVhdGVkIGF0IDIwMTAtMDktMDIgMTE6MTg6NTMtMDQwMDAeFw0xMDA5MDgyMjAy
MjZaFw0yMDA5MDgyMjAyMjZaMH8xFzAVBgNVBAoTDnJQYXRoIHJCdWlsZGVyMRkw
FwYDVQQLExBodHRwOi8vcnBhdGguY29tMUkwRwYDVQQDFEBsb2NhbF91dWlkOmxv
Y2FsdXVpZDAwMSBnZW5lcmF0ZWRfdXVpZDpnZW5lcmF0ZWR1dWlkMDAxIHNlcmlh
bDowMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArjQwIwV1EcuiCkUz
0lT/FTvP+HrAeK8UJ89uFCwHrvFvAI1SQbsUKxaeaOcn4Xv5k8bt3GtXS8dFrk0I
eTCpEi+gMkjE8OtXnLoJpmeXY9PMf94+/jYvvPEPSPs0Y93THKryWN3qpzpwtyLK
hN1eLIezxfaphgHeqBk0ySqoQ7/moE6DUFpHScUY8xRoEKc8jgQGAyyv165zXNp4
XDmeuFMdPjjh1/XZI3oeEJaSWpGeIGgsGRG3RtaoJ3hkSDalijE68rY59hlVYzZa
VoQ2+2TPnyhHERR5ZeEWq18FP5IFcnrO00jbmXN7J+lTeC7xSd5raEBLA/PlzzEE
L1sRTwIDAQABoxAwDjAMBgNVHRMBAf8EAjAAMA0GCSqGSIb3DQEBBQUAA4IBAQDI
cpBRkPR43fvI34XQ+Y8cwcmqQAGYpGX3RNYbg1HitgK3udsrj18vy7NdLLVxqvxE
OBjk2JmWACzPLr3d8tZxJ5xErkvS19B6yTPmDJ/urgjvt+kP16STZyHYRdtjTQky
SD1yGxq53fEeQJ4xr4jpgkjG978XjyW3kdWh9CYKwi6n1ls3PYKb8/eqXcdf33rQ
aSGSALLCk6/Y/GnUX7+swXg+l2h6qEmLC3gpm7rnbwPc/IR3D+gNITa//GrEhYY9
QxPgKzSzo2neRkgVwj7jGxr+R6ohRAawzQYfCzk01ZAUKakrvDrrLXob5fwUeWAr
1T5mV6JdQRbN6mD7t7U2
-----END CERTIFICATE-----
"""
