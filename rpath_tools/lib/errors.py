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



class SystemModelServiceError(Exception):
    "Base class"

class InstallationServiceError(Exception):
    "Base class"

class NoUpdatesFound(InstallationServiceError):
    "Raised when no updates are available"

class RepositoryError(InstallationServiceError):
    "Raised when a repository error is caught"

class FrozenJobPathMissing(SystemModelServiceError):
    "Raise when the path to a frozen job is missing"

class FrozenUpdateJobError(SystemModelServiceError):
    "Raise when a freezing an update job fails"

class BuildUpdateJobError(SystemModelServiceError):
    "Raise when building an update job fails"

class NotImplementedError(SystemModelServiceError):
    "Raise when a function is not implemented"
