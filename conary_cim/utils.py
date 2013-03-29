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


"""Python Provider for RPATH_UpdateConcreteJob

Instruments the CIM class RPATH_UpdateConcreteJob

"""

import time

class Time(object):
    timeFormat = "%%Y%%m%%d%%H%%M%%S.%06d+000"

    @classmethod
    def format(cls, tstamp):
        if tstamp is None:
            return None
        tstamp = float(tstamp)
        microsec = int((tstamp - int(tstamp)) * 1e6)
        return time.strftime(cls.timeFormat % microsec, time.gmtime(tstamp))
