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


import sys
import logging

class Logger(object):
    __slots__ = [ 'log_error', 'log_info', 'log_warn', 'log_debug', ]
    _logger = None

    def __new__(cls, *args, **kwargs):
        if cls._logger is None:
            cls._logger = object.__new__(cls)
        return cls._logger

    def __init__(self, name, logFile, debug=False):
        self.newLogger(name, logFile)
        self.setDebug(debug)
        self.log_info = self.logger.info
        self.log_error = self.logger.error
        self.log_warn = self.logger.warn
        self.log_debug = self.logger.debug

    def setDebug(self, debug):
        self.logger.removeHandler(self.debugHandler)
        if debug:
            self.logger.addHandler(self.debugHandler)
            logLevel = logging.DEBUG
        else:
            logLevel = logging.INFO
        self.logger.setLevel(logLevel)

    @classmethod
    def newLogger(cls, name, logFile):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logFile)
        formatter = logging.Formatter("%(asctime)s - %(levelname)-8s %(name)-15s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)

        cls.logger = logger
        cls.debugHandler = streamHandler
