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

from conary.lib import mainhandler

from rpath_tools.client import command
from rpath_tools.client import config
from rpath_tools.client import constants
from rpath_tools.client import errors

class rRegisterMain(mainhandler.MainHandler):

    name = 'rregister'
    version = constants.version

    abstractCommand = command.rRegisterCommand
    configClass = config.rRegisterConfiguration
    commandList = [command.RegistrationCommand, command.HardwareCommand,
                   command.ConfigCommand]

    setSysExcepthook = False

    def configureLogging(self, logFile, debug):
        global logger
        logger = logging.getLogger('registration')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logFile)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if debug:
            logger.setLevel(logging.DEBUG)
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(formatter)
            logger.addHandler(streamHandler)

        logger.info("Starting run of registration client...")

    def runCommand(self, command, *args, **kw):
        cfg = args[0]
        self.configureLogging(cfg.logFile, cfg.debugMode)
        logger.info("Running command: %s" % command.commands[0])
        response = mainhandler.MainHandler.runCommand(self, command, *args, **kw)
        logger.info('Registration client exiting.')
        return response

def _main(argv, MainClass):
    """
    Wrapper method that handles all remaining uncaught exceptions from
    rregister..
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
            debuggerException = errors.rRegisterInternalError
        sys.excepthook = errors.genExcepthook(debug=debugAll,
                                              debugCtrlC=debugAll)
        rc = MainClass().main(argv, debuggerException=debuggerException)
        if rc is None:
            return 0
        return rc
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
    Python hook for starting rregister from the command line.
    @param argv: standard argument vector
    """
    return _main(argv, rRegisterMain)