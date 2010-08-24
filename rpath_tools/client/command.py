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
import os
import sys
import time
import StringIO

from conary.lib import command
from conary.lib import options

from rpath_models import System, Networks, Network
from rpath_tools.client import hardware
from rpath_tools.client import register
from rpath_tools.client.utils import client

logger = logging.getLogger('client')

class RpathToolsCommand(command.AbstractCommand):
    def runCommand(self, *args, **kw):
        pass

class RegistrationCommand(RpathToolsCommand):
    commands = ['register']
    help = 'register the system with rBuilder'
    requireConfig = True

    def addParameters(self, argDef):
        RpathToolsCommand.addParameters(self, argDef)
        argDef['check'] = options.NO_PARAM
        argDef['force'] = options.NO_PARAM
        argDef['boot'] = options.NO_PARAM
        argDef['shutdown'] = options.NO_PARAM
        
    def checkRegistrationDisabled(self):
        exists = os.path.exists(self.cfg.disableRegistrationFilePath)
        if exists:
            logger.info('Registration disable file exists at (%s). Not registering.' \
                % self.cfg.disableRegistrationFilePath)
        else:
            logger.debug('Registration disable file does not exist at (%s).' \
                % self.cfg.disableRegistrationFilePath)

        return exists

    def _checkTimeout(self, timeoutFile, timeout):
        try:
            f = open(timeoutFile)
        except IOError, e:
            # If the file was not found, be safe and assume we need to
            # register
            logger.error("Could not open file %s for reading." % timeoutFile)
            return True
        tStamp = f.read().strip()
        tStamp = int(float(tStamp))
        logger.debug("Timestamp of %s read from %s." % (str(tStamp),
            timeoutFile))
        if (time.time() - timeout) > tStamp:
            logger.debug("Timeout exceeded.")
            return True
        logger.debug("Timeout not exceeded.")
        return False

    def checkPollTimeout(self):
        timedOut = self._checkTimeout(self.cfg.lastPollFilePath,
                self.cfg.contactTimeoutInterval * 60 * 60)
        if timedOut:
            logger.info('Poll timeout exceeded, running registration.')
            print 'Poll timeout exceeded, running registration.'
        else:
            logger.info('Poll timeout not exceeded.')
        return timedOut

    def checkRegistrationTimeout(self):
        timedOut = self._checkTimeout(self.cfg.lastRegistrationFilePath,
                self.cfg.registrationInterval * 60 * 60)
        if timedOut:
            logger.info('Registration interval exceeded, running registration.')
            print 'Registration interval exceeded, running registration.'
        else:
            logger.info('Registration interval not exceeded.')
        return timedOut

    def shouldRun(self):
        registrationDisabled = self.checkRegistrationDisabled()

        if registrationDisabled:
            return False

        if self.boot and self.cfg.bootRegistration:
            logger.info('--boot specified and bootRegistration is True, running registration')
            return True

        if self.force:
            logger.info('--force specified, running registration')
            return True

        if self.shutdown:
            logger.info('--shutdown specified, running registration')
            return True

        return self.checkPollTimeout() or self.checkRegistrationTimeout()

    def runCommand(self, cfg, argSet, args):
        self.cfg = cfg
        self.check = argSet.pop('check', False)
        self.force = argSet.pop('force', False)
        self.boot = argSet.pop('boot', False)
        self.shutdown = argSet.pop('shutdown', False)

        if not self.shouldRun():
            print 'Registration not needed.'
            logger.info('Registration Client will not run, exiting.')
            sys.exit(2)
        else:
            print 'Registration needed.'

        registration = register.Registration(self.cfg)
        hwData = hardware.HardwareData(self.cfg.sfcbUrl)

        sslClientCertPath, sslClientKeyPath = registration.readCredentials()
        sslClientCert = file(sslClientCertPath).read()
        sslClientKey = file(sslClientKeyPath).read()
        sslServerCert = file(registration.sslCertificateFilePath).read()
        agentPort = int(registration.sfcbConfig.get('httpsPort', 5989))

        try:
            ips = hwData.getIpAddresses()
            hostname = hwData.getHostname()
        except Exception, e:
            logger.error("Error fetching network information of system")
            raise e

        if self.shutdown:
            state = 'shut_down'
        else:
            state = 'registerd'

        system = System.factory(name=hostname, description=hostname,
                                generated_uuid=registration.generatedUuid,
                                local_uuid=registration.localUuid, 
                                ssl_client_certificate=sslClientCert,
                                ssl_client_key=sslClientKey, 
                                ssl_server_certificate=sslServerCert,
                                state=state,
                                registerd=True,
                                agent_port = agentPort
                                )

        localIp = hwData.getLocalIp(self.cfg.directMethod)
        networks = Networks.factory()
        requiredIp = self.cfg.requiredNetwork or object()
        for ip in ips:
            network = Network.factory(ip_address=ip.ipv4,
                netmask = ip.netmask,
                dns_name=ip.dns_name, active=(ip.ipv4 == localIp),
                required = (requiredIp in [ ip.ipv4, ip.dns_name ] or None),
                device_name=ip.device)
            networks.add_network(network)
        system.set_networks(networks)
        logger.info('Registering System with local uuid %s and generated '
                    'uuid %s' % (system.local_uuid, system.generated_uuid))
        print "Registering system...",
        success = registration.registerSystem(system)
        if not success:
            print 'Failure'
            return 1
        print 'Complete.'
        return 0

class HardwareCommand(RpathToolsCommand):
    commands = ['hardware']
    help = "get the system's hardware information via CIM."
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        hwData = hardware.main(self.cfg)
        return hwData

class ConfigCommand(RpathToolsCommand):
    commands = ['config']
    help = 'Display the current configuration'
    
    def runCommand(self, cfg, argSet, args, **kwargs):
        try:
            prettyPrint = sys.stdout.isatty()
        except AttributeError:
            prettyPrint = False
        cfg.setDisplayOptions(hidePasswords=True,
                              showContexts=False,
                              prettyPrint=True,
                              showLineOrigins=False)
        if argSet: return self.usage()
        if (len(args) > 2):
            return self.usage()
        else:
            cfg.display()
