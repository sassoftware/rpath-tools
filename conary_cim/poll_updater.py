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


import time

from rpath_tools.client import config

def updatePollFile(logger=None):
    try:
        rPathToolsConfig = config.RpathToolsConfiguration(readConfigFiles=True)
        pollFile = open(rPathToolsConfig.lastPollFilePath, 'w')
        pollFile.write(str(time.time()))
        pollFile.close()
    except Exception, e:
        if logger:
            logger.log_error('Failed updating poll file at %s' % \
                rPathToolsConfig.lastPollFilePath)
            logger.log_error(str(e))
