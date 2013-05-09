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
import traceback

from conary.lib import util

logger = logging.getLogger("client")

class RpathToolsError(Exception):
    msg_prefix = '\n'
    msg = "ERROR: An error has occurred in rpath-tools: %s."

    def __init__(self, exception):
        self.exception = exception

    def __str__(self):
        return self.msg_prefix + self.msg % str(self.exception)

class RpathToolsRegistrationError(RpathToolsError):
    msg = "ERROR: An error has occurred in rpath-tools during registration: %s."

class RpathToolsInternalError(RpathToolsError):
    pass

_ERROR_MESSAGE = '''
ERROR: An unexpected condition has occurred in rpath-tools.  This is
most likely due to insufficient handling of erroneous input, but
may be some other bug.  In either case, please report the error at
https://issues.rpath.com/ and attach to the issue the file
%(stackfile)s

To get a debug prompt, rerun the command with the --debug-all argument.

For more information, go to:
http://wiki.rpath.com/wiki/Conary:How_To_File_An_Effective_Bug_Report
For more debugging help, please go to #conary on freenode.net
or email conary-list@lists.rpath.com.

Error details follow:

%(filename)s:%(lineno)s
%(errtype)s: %(errmsg)s

The complete related traceback has been saved as %(stackfile)s
'''

def genExcepthook(*args, **kw):
    #pylint: disable-msg=C0999
    # just passes arguments through
    """
    Generates an exception handling hook that brings up a debugger.

    A full traceback will be output in C{/tmp}.

    Example::
        sys.excepthook = genExceptHook(debugAll=True)
    """

    #pylint: disable-msg=C0103
    # follow external convention
    def excepthook(e_type, e_value, e_traceback):
        """Exception hook wrapper"""
        logger.error("An exception has occurred: %s" % e_value)
        logger.error(''.join(traceback.format_tb(e_traceback)))
        baseHook = util.genExcepthook(error=_ERROR_MESSAGE,
            prefix='rpath-tools-error-', *args, **kw)

        baseHook(e_type, e_value, e_traceback)

    return excepthook
