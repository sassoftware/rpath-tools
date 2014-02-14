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
import sys
from conary.lib import command, options

from rpath_tools.client import updater
from rpath_tools.client.utils.collector import Collector
from rpath_tools.client.utils.informer import Informer

logger = logging.getLogger(__name__)

commandList = []


class RpathToolsCommand(command.AbstractCommand):

    def addParameters(self, argDef):
        command.AbstractCommand.addParameters(self, argDef)
        argDef['quiet'] = options.NO_PARAM

    def runCommand(self, *args, **kw):
        pass


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
commandList.append(ConfigCommand)


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
commandList.append(HelpCommand)


class UpdateCommand(RpathToolsCommand):
    commands = ['updater', 'preview', 'apply', 'install', 'update', 'updateall',]
    help = "Run updates on the local host."
    requireConfig = True

    def addParameters(self, argDef):
        RpathToolsCommand.addParameters(self, argDef)
        argDef['item'] = options.MULT_PARAM
        argDef['jobid'] = options.ONE_PARAM
        argDef['xml'] = options.NO_PARAM
        argDef['json'] = options.NO_PARAM

    def shouldRun(self):
        if len(self.commands) != 1:
            logger.error('specify only one command action : %s' % 
                                ' '.join(self.command_types))
            return False
        if 'apply' in self.commands and not self.jobid:
            logger.error('apply command requires --jobid <jobid string>')
            return False
        if 'preview' in self.commands and not [ x for x in self.tlis if x ]:
            logger.error('preview command requires --item <trove spec>')
            return False
        if 'update' in self.commands and not [ x for x in self.tlis if x ]:
            logger.error('update command requires --item <trove spec>')
            return False
        return True


    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        argSet = args[1]
        self.tlis = argSet.pop('item', [])
        self.jobid = argSet.pop('jobid', None)
        self.xml = argSet.pop('xml', False)
        self.json = argSet.pop('json', False)
        self.command_types = ['preview', 'apply', 'install', 'update', 'updateall' ]
        self.commands = [ x for x in args[-1] if x in self.command_types ]

        if not self.shouldRun():
            logger.info('Updater will not run, exiting.')
            sys.exit(2)

        up = updater.Updater()
        if 'apply' in self.commands and self.jobid:
            results = up.cmdlineApply(self.jobid, self.xml, self.json)
        else:
            results = up.cmdlineUpdate(self.tlis, self.commands, self.xml, self.json)
        return results
commandList.append(UpdateCommand)


class CollectorCommand(RpathToolsCommand):
    commands = ['collector']
    help = "Collect log and config files on the local host."
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        collector = Collector()
        results = collector.collect()
        return results
commandList.append(CollectorCommand)


class InformerCommand(RpathToolsCommand):
    commands = ['informer', 'top', 'updates', 'counter' ]
    help = "Gather conary information about the local host including top level items and available updates"
    requireConfig = True

    def runCommand(self, *args, **kw):
        self.cfg = args[0]
        self.command_types = [ 'top', 'updates', 'counter', ]
        self.values = [ x for x in args[-1] if x in self.command_types ]
        informer = Informer(self.values)
        results = informer.inform()
        return results
commandList.append(InformerCommand)
