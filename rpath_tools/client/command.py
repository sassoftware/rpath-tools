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
import os
import random
import subprocess
import sys
import time

from conary.lib import command, options

from rpath_models import System, Networks, Network, CurrentState, ManagementInterface
from rpath_tools.client import hardware
from rpath_tools.client import register
from rpath_tools.client import scan
from rpath_tools.client import updater
from rpath_tools.client import configurator
from rpath_tools.client.sysdisco import puppet



from rpath_tools.client.utils.tmpwatcher import TmpWatcher
from rpath_tools.client.utils.collector import Collector
from rpath_tools.client.utils.informer import Informer

logger = logging.getLogger('client')

class RpathToolsCommand(command.AbstractCommand):

    def addParameters(self, argDef):
        command.AbstractCommand.addParameters(self, argDef)
        argDef['quiet'] = options.NO_PARAM

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
        argDef['event-uuid'] = options.ONE_PARAM
        argDef['random-wait'] = options.NO_PARAM

    def checkRegistrationDisabled(self):
        exists = os.path.exists(self.cfg.disableRegistrationFilePath)
        if exists:
            logger.info('Registration disable file exists at (%s). Not registering.' \
                % self.cfg.disableRegistrationFilePath)
        else:
            logger.debug('Registration disable file does not exist at (%s).' \
                % self.cfg.disableRegistrationFilePath)

        return exists

    def checkRandomWait(self):
        exists = os.path.exists(self.cfg.randomWaitFilePath)
        if exists:
            logger.info('Random wait file exists at (%s).' \
                % self.cfg.randomWaitFilePath)
            randomWait = int(open(self.cfg.randomWaitFilePath).read())
        else:
            logger.info('Random wait file does not exist at (%s).' \
                % self.cfg.randomWaitFilePath)
            randomWait = int(random.random() * self.cfg.randomWaitMax)
            logger.info('Writing random wait value of (%s) to (%s).' \
                % (randomWait, self.cfg.randomWaitFilePath))
            f = open(self.cfg.randomWaitFilePath, 'w')
            f.write(str(randomWait))
            f.close()

        logger.info('Sleeping for random wait value of (%s) seconds...' \
            % randomWait)
        time.sleep(randomWait)
        logger.info('Waking up after sleeping for (%s) seconds.' \
            % randomWait)

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
        else:
            logger.info('Poll timeout not exceeded.')
        return timedOut

    def checkRegistrationTimeout(self):
        timedOut = self._checkTimeout(self.cfg.lastRegistrationFilePath,
                self.cfg.registrationInterval * 60 * 60)
        if timedOut:
            logger.info('Registration interval exceeded, running registration.')
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
        self.event_uuid = argSet.pop('event-uuid', None)
        self.randomWait = argSet.pop('random-wait', None)

        if not self.shouldRun():
            logger.info('Registration Client will not run, exiting.')
            sys.exit(2)

        if self.randomWait:
            logger.debug('--random-wait specified.')
            self.checkRandomWait()

        hwData = hardware.HardwareData(self.cfg)
        registration = register.Registration(self.cfg)
        remote = registration.getRemote()
        # Just use the first remote server found to look up the localIp
        localIp = hwData.getLocalIp(remote)
        deviceName = hwData.getDeviceName(localIp)
        registration.setDeviceName(deviceName)

        if not remote:
            msg = "No remote server found to register with.  " + \
                "Check that either directMethod or slpMethod is configured correctly."
            logger.error(msg)
            sys.exit(2)


        sslServerCert = file(registration.sslCertificateFilePath).read()
        agentPort = int(registration.sfcbConfig.get('httpsPort', 5989))

        try:
            ips = hwData.getIpAddresses()
            hostname = hwData.getHostname()
        except Exception, e:
            logger.error("Error fetching hardware information of system")
            logger.error(e)
            raise e

        if self.shutdown:
            state = 'non-responsive-shutdown'
        else:
            state = 'registered'


        networks = Networks.factory()
        requiredIp = self.cfg.requiredNetwork or object()
        for ip in ips:
            active = (ip.ipv4 == localIp)
            network = Network.factory(ip_address=ip.ipv4,
                netmask = ip.netmask,
                dns_name=ip.dns_name, active=active,
                required = (requiredIp in [ ip.ipv4, ip.dns_name ] or None),
                device_name=ip.device)
            networks.add_network(network)

        current_state = CurrentState(name=state)
        management_interface = ManagementInterface(name='cim')
        system = System(hostname=hostname,
                        generated_uuid=registration.generatedUuid,
                        local_uuid=registration.localUuid,
                        ssl_server_certificate=sslServerCert,
                        current_state=current_state,
                        agent_port=agentPort,
                        event_uuid=self.event_uuid,
                        management_interface=management_interface)
        bootUuidFilePath = cfg.bootUuidFilePath
        if self.boot and os.path.exists(bootUuidFilePath):
            bootUuid = file(bootUuidFilePath).read().strip()
            system.set_boot_uuid(bootUuid)
        if registration.targetSystemId:
            system.set_target_system_id(registration.targetSystemId)

        system.set_networks(networks)
        logger.info('Registering System with local uuid %s and generated '
                    'uuid %s' % (system.local_uuid, system.generated_uuid))
        success = registration.registerSystem(system)
        if not success:
            logger.error("Registration failed")
            return 1
        self._cleanup()
        logger.info("Registration complete")
        return 0

    def _cleanup(self):
        if self.boot and os.path.exists(self.cfg.bootUuidFilePath):
            os.unlink(self.cfg.bootUuidFilePath)

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
        cfg.setDisplayOptions(hidePasswords=True,
                              showContexts=False,
                              prettyPrint=True,
                              showLineOrigins=False)
        if argSet: return self.usage()
        if (len(args) > 2):
            return self.usage()
        else:
            cfg.display()

class HelpCommand(RpathToolsCommand):
    """
    Displays help about this program or commands within the program.
    """
    commands = ['help']
    help = 'Display help information'

    def runCommand(self, cfg, argSet, args, **kwargs):
        command, subCommands = self.requireParameters(args, allowExtra=True)
        if subCommands:
            command = subCommands[0]
            commands = self.mainHandler._supportedCommands
            if not command in commands:
                print >> sys.stderr, "%s: no such command: '%s'" % (
                        self.mainHandler.name, command)
                sys.exit(1)
            print >> sys.stderr, commands[command].usage()
        else:
            print >> sys.stderr, self.mainHandler.usage()

class IConfigCommand(RpathToolsCommand):
    commands = ['iconfig']
    help = 'Apply the instance configuration'

    def runCommand(self, cfg, argSet, args, **kwargs):
        cmd = ['/usr/sbin/iconfig']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        sts = p.wait()
        print p.stdout.read()
        return sts


class ScanCommand(RpathToolsCommand):
    commands = ['scan', 'toplevelitems']
    help = "Run a survey on the local host."
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        self.tli = args[-1]
        results = scan.main(self.cfg, self.tli)
        return results

class UpdateCommand(RpathToolsCommand):
    commands = ['updater', 'preview', 'apply', 'install', 'update', 'updateall',]
    help = "Run updates on the local host."
    requireConfig = True

    def addParameters(self, argDef):
        RpathToolsCommand.addParameters(self, argDef)
        argDef['preview'] = options.ONE_PARAM
        argDef['apply'] = options.ONE_PARAM
        argDef['install'] = options.ONE_PARAM
        argDef['update'] = options.ONE_PARAM
        argDef['updateall'] = options.NO_PARAM



    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        self.tli = args[-1]
        self.jobid = None
        if 'jobid' in args:
            self.jobid = args.pop('jobid', None)
        self.command_types = ['update', 'preview', 'apply', 'updateall', 'install']
        self.commands = [ x for x in args[-1] if x in self.command_types ]
        if 'apply' in self.commands and self.jobid:
            updater.apply(self.cfg, self.commands, self.iid)
        results = updater.preview(self.cfg, self.commands, self.tli)
        return results


class ConfiguratorCommand(RpathToolsCommand):
    commands = ['configurator', 'read', 'write', 'validate', 'discover']
    help = "Run configurators on the local host."
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        self.command_types = [ 'read', 'write', 'validate', 'discover' ]
        self.configurators = [ x for x in args[-1] if x in self.command_types ]
        configurator.main(self.cfg, self.configurators)
        ruppet = puppet.Puppet()
        pc = ruppet.run(logger)
        return pc


class TmpWatchCommand(RpathToolsCommand):
    commands = ['tmpwatch', 'delete']
    help = "Delete surveys older than 10 days on the local host."
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        delete = False
        if [ x for x in args[-1] if x == 'delete']:
            delete = True
        prefix = 'survey-'
        mtime = 10
        if os.path.exists(self.cfg.scannerSurveyStore):
            watch = TmpWatcher(self.cfg.scannerSurveyStore, mtime=mtime, prefix=prefix)
            removed = watch.clean(delete=delete)
            if not delete:
                print 'Files to remove:'
                print '\n'.join(removed)
            return 0
        return 2

class CollectorCommand(RpathToolsCommand):
    commands = ['collector']
    help = "Collect log and config files on the local host."
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        collector = Collector()
        results = collector.collect()
        return results

class InformerCommand(RpathToolsCommand):
    commands = ['informer', 'top', 'updates', 'counter' ]
    help = "Gather conary information about the local host"
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        self.command_types = [ 'top', 'updates', 'counter', ]
        self.values = [ x for x in args[-1] if x in self.command_types ]
        informer = Informer(self.values)
        results = informer.inform()
        return results

