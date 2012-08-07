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


import errno
import logging
import sys

from conary.lib import log as cny_log
from conary.lib import mainhandler

from rpath_tools.client import command
from rpath_tools.client import config
from rpath_tools.client import constants
from rpath_tools.client import errors

logger = logging.getLogger('client')


class RpathToolsMain(mainhandler.MainHandler):

    name = 'rpath-tools'
    version = constants.version

    abstractCommand = command.RpathToolsCommand
    configClass = config.RpathToolsConfiguration
    commandList = [command.RegistrationCommand, command.HardwareCommand,
                   command.ConfigCommand, command.HelpCommand,
                   command.IConfigCommand, command.ScanCommand,
                   command.ConfiguratorCommand, command.TmpWatchCommand, ]

    setSysExcepthook = False

    def configureLogging(self, logFile, debug, quiet):
        if debug:
            consoleLevel = logging.DEBUG
            fileLevel = logging.DEBUG
        elif quiet:
            consoleLevel = logging.ERROR
            fileLevel = logging.INFO
        else:
            consoleLevel = logging.INFO
            fileLevel = logging.INFO
        cny_log.setupLogging(
                logPath=logFile,
                consoleLevel=consoleLevel,
                consoleFormat='apache',
                fileLevel=fileLevel,
                fileFormat='apache',
                logger='client',
                )

    def runCommand(self, command, cfg, argSet, *args, **kw):
        debug = cfg.debugMode
        quiet = argSet.get('quiet', False)
        self.configureLogging(cfg.logFile, debug, quiet)
        logger.info("Running command: %s" % command.commands[0])
        response = mainhandler.MainHandler.runCommand(self, command, cfg,
                argSet, *args, **kw)
        logger.info("Command finished: %s" % command.commands[0])
        return response

def _main(argv, MainClass):
    """
    Wrapper method that handles all remaining uncaught exceptions from
    rpath-tools.

    @param argv: standard argument vector
    @param MainClass: class object that implements a main() method.
    """
    if argv is None:
        argv = sys.argv
    #pylint: disable-msg=E0701
    # pylint complains about except clauses here because we sometimes
    # redefine debuggerException
    debuggerException = Exception
    try:
        argv = list(argv)
        debugAll = '--debug-all' in argv
        if debugAll:
            argv.remove('--debug-all')
        else:
            debuggerException = errors.RpathToolsError
        sys.excepthook = errors.genExcepthook(debug=debugAll,
                                              debugCtrlC=debugAll)
        rc = MainClass().main(argv, debuggerException=debuggerException)
        if rc is None:
            return 0
        return rc
    except errors.RpathToolsError, e:
        print e
        return 1
    except debuggerException, err:
        raise
    except IOError, e:
        # allow broken pipe to exit
        if e.errno != errno.EPIPE:
            raise
    except KeyboardInterrupt:
        return 1
    return 0

def main(argv=None):
    """
    Python hook for starting rpath from the command line.
    @param argv: standard argument vector
    """
    return _main(argv, RpathToolsMain)
