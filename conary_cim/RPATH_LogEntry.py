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


"""Python Provider for RPATH_LogEntry

Instruments the CIM class RPATH_LogEntry

"""

import pywbem

import concrete_job
import utils
import stub_RPATH_LogEntry
import RPATH_RecordLog

stubClass = stub_RPATH_LogEntry.RPATH_LogEntry

class RPATH_LogEntry(stubClass):
    def __init__ (self, env):
        stubClass.__init__(self, env)

    def get_instance(self, env, model):
        """Return an instance.

        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        model -- A template of the pywbem.CIMInstance to be returned.  The 
            key properties are set on this instance to correspond to the 
            instanceName that was requested.  The properties of the model
            are already filtered according to the PropertyList from the 
            request.  Only properties present in the model need to be
            given values.  If you prefer, you can set all of the 
            values, and the instance will be filtered for you. 

        Possible Errors:
        CIM_ERR_ACCESS_DENIED
        CIM_ERR_INVALID_PARAMETER (including missing, duplicate, unrecognized 
            or otherwise incorrect parameters)
        CIM_ERR_NOT_FOUND (the CIM Class does exist, but the requested CIM 
            Instance does not exist in the specified namespace)
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.get_instance()' \
                % self.__class__.__name__)

        jobId, logEntryTimestamp = self.fromInstanceID(model['InstanceID'])
        concreteJob = concrete_job.AnyJob.load(jobId)
        cuJob = concreteJob.concreteJob
        logEntries = [ x for x in cuJob.logs.enumerate()
            if x.timestamp == logEntryTimestamp ]
        if not logEntries:
            return
        logEntry = logEntries[0]

        created = utils.Time.format(logEntryTimestamp)

        #model['Caption'] = '' # TODO 
        model['CreationTimeStamp'] = pywbem.CIMDateTime(created)
        #model['Description'] = '' # TODO 
        #model['ElementName'] = '' # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['Locale'] = '' # TODO 
        model['LogInstanceID'] = self.createLogInstanceID(jobId)
        #model['LogName'] = '' # TODO 
        #model['Message'] = logEntry.content
        #model['MessageArguments'] = [ logEntry.content ]
        #model['MessageID'] = '' # TODO 
        #model['OwningEntity'] = '' # TODO 
        model['PerceivedSeverity'] = self.Values.PerceivedSeverity.Information
        model['RecordData'] = logEntry.content
        model['RecordFormat'] = ''
        model['RecordID'] = model['InstanceID']
        return model

    def enum_instances(self, env, model, keys_only):
        """Enumerate instances.

        The WBEM operations EnumerateInstances and EnumerateInstanceNames
        are both mapped to this method. 
        This method is a python generator

        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        model -- A template of the pywbem.CIMInstances to be generated.  
            The properties of the model are already filtered according to 
            the PropertyList from the request.  Only properties present in 
            the model need to be given values.  If you prefer, you can 
            always set all of the values, and the instance will be filtered 
            for you. 
        keys_only -- A boolean.  True if only the key properties should be
            set on the generated instances.

        Possible Errors:
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.enum_instances()' \
                % self.__class__.__name__)

        # Prime model.path with knowledge of the keys, so key values on
        # the CIMInstanceName (model.path) will automatically be set when
        # we set property values on the model. 
        model.path.update({'InstanceID': None})

        for job in concrete_job.AnyJob.list():
            logInstanceID = self.createLogInstanceID(job.keyId)
            model['LogInstanceID'] = logInstanceID
            for le in job.logs.enumerate():
                model['InstanceID'] = self.createInstanceID(job.keyId, le.timestamp)
                if keys_only:
                    yield model
                else:
                    try:
                        yield self.get_instance(env, model)
                    except pywbem.CIMError, (num, msg):
                        if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                       pywbem.CIM_ERR_ACCESS_DENIED):
                            raise

    @classmethod
    def createLogInstanceID(cls, resourceId):
        return RPATH_RecordLog.RPATH_RecordLog.createInstanceID(resourceId)

    @classmethod
    def createInstanceID(cls, resourceId, timestamp):
        return 'com.rpath:recordLogs/%s:%s' % (resourceId, timestamp)

    @classmethod
    def fromInstanceID(cls, instanceId):
        localId = instanceId.split(':', 1)[-1]
        # Strip leading recordLogs
        localId = localId.split('/', 1)[-1]
        return localId.split(':', 1)

def get_providers(env):
    rpath_logentry_prov = RPATH_LogEntry(env)
    return {'RPATH_LogEntry': rpath_logentry_prov}
