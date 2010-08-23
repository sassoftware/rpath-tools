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
from ractivate import hardware
from ractivate import activate
from ractivate.utils import client

logger = logging.getLogger('activation')

class rActivateCommand(command.AbstractCommand):
    def runCommand(self, *args, **kw):
        pass

class ActivationCommand(rActivateCommand):
    commands = ['activate']
    help = 'activate the system with XX/rBA'
    requireConfig = True

    def addParameters(self, argDef):
        rActivateCommand.addParameters(self, argDef)
        argDef['check'] = options.NO_PARAM
        argDef['force'] = options.NO_PARAM
        argDef['boot'] = options.NO_PARAM
        argDef['shutdown'] = options.NO_PARAM
        
    def checkActivationDisabled(self):
        exists = os.path.exists(self.cfg.disableActivationFilePath)
        if exists:
            logger.info('Activation disable file exists (%s). Not activating.' \
                % self.cfg.disableActivationFilePath)
        else:
            logger.debug('Activation disable file does not exist (%s).' \
                % self.cfg.disableActivationFilePath)

        return exists

    def _checkTimeout(self, timeoutFile, timeout):
        try:
            f = open(timeoutFile)
        except IOError, e:
            # If the file was not found, be safe and assume we need to
            # activate
            logger.error("Could not open file %s for reading." % timeoutFile)
            return True
        tStamp = f.read().strip()
        tStamp = int(float(tStamp))
        if (time.time() - timeout) > tStamp:
            return True
        return False

    def checkPollTimeout(self):
        timedOut = self._checkTimeout(self.cfg.lastPollFilePath,
                self.cfg.contactTimeoutInterval * 60 * 60)
        if timedOut:
            logger.info('Poll timeout exceeded, running activation.')
        else:
            logger.info('Poll timeout not exceeded.')
        return timedOut

    def checkActivationTimeout(self):
        timedOut = self._checkTimeout(self.cfg.lastActivationFilePath,
                self.cfg.activationInterval * 60 * 60)
        if timedOut:
            logger.info('Activation interval exceeded, running activation.')
        else:
            logger.info('Activation interval not exceeded.')
        return timedOut

    def shouldRun(self):
        activationDisabled = self.checkActivationDisabled()

        if activationDisabled:
            return False

        if self.boot and self.cfg.bootActivation:
            return True

        if self.force or self.shutdown:
            return True

        return self.checkPollTimeout() or self.checkActivationTimeout()

    def runCommand(self, cfg, argSet, args):
        self.cfg = cfg
        self.check = argSet.pop('check', False)
        self.force = argSet.pop('force', False)
        self.boot = argSet.pop('boot', False)
        self.shutdown = argSet.pop('shutdown', False)

        if not self.shouldRun():
            print 'Activation not needed.'
            logger.info('Activation Client will not run, exiting.')
            sys.exit(2)
        else:
            print 'Activation needed...'

        activation = activate.Activation(self.cfg)
        hwData = hardware.HardwareData(self.cfg.sfcbUrl)

        sslClientCertPath, sslClientKeyPath = activation.readCredentials()
        sslClientCert = file(sslClientCertPath).read()
        sslClientKey = file(sslClientKeyPath).read()
        sslServerCert = file(activation.sslCertificateFilePath).read()
        agentPort = int(activation.sfcbConfig.get('httpsPort', 5989))

        try:
            ips = hwData.getIpAddresses()
            hostname = hwData.getHostname()
        except Exception, e:
            logger.error("Error fetching network information of system")
            raise e

        if self.shutdown:
            state = 'shut_down'
        else:
            state = 'activated'

        system = System.factory(name=hostname, description=hostname,
                                generated_uuid=activation.generatedUuid,
                                local_uuid=activation.localUuid, 
                                ssl_client_certificate=sslClientCert,
                                ssl_client_key=sslClientKey, 
                                ssl_server_certificate=sslServerCert,
                                state=state,
                                activated=True,
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
        logger.info('Activating System with local uuid %s and generated '
                    'uuid %s' % (system.local_uuid, system.generated_uuid))
        success = activation.activateSystem(system)
        if not success:
            print 'Failure'
            return 1
        print 'Complete.'
        return 0

class HardwareCommand(rActivateCommand):
    commands = ['hardware']
    help = "get the system's hardware information via CIM."
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        hwData = hardware.main(self.cfg)
        return hwData

class ConfigCommand(rActivateCommand):
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
