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


from conary.cmds import updatecmd


class JsonUpdateCallback(updatecmd.JsonUpdateCallback):
    class LogStream(object):
        def __init__(self, job):
            self.job = job
            self.json_logs = []

        def write(self, text):
            if text.startswith('{'):
                self.json_logs.append(text)
            self.job.logs.add(text)

    def __init__(self, job):
        updatecmd.JsonUpdateCallback.__init__(self)
        self.job = job
        self.out = self.LogStream(job)

    def _message(self, text):
        if not text:
            return
	self.out.write(text)

    def done(self):
        self.out.write("Done")
    updateDone = done


class UpdateCallback(updatecmd.UpdateCallback):
    class LogStream(object):
        def __init__(self, job):
            self.job = job
        def write(self, text):
            self.job.logs.add(text)

    def __init__(self, job):
        updatecmd.UpdateCallback.__init__(self)
        self.job = job
        self.out = self.LogStream(job)

    def _message(self, text):
        if not text:
            return
        self.job.logs.add(text)

    def done(self):
        self.job.logs.add("Done")
    updateDone = done



