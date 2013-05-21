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


import pywbem
import utils

class ConcreteJobMixIn(object):
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

        key = self.fromInstanceID(model['InstanceID'])
        task = self._task.load(key)
        cuJob = task.job
        if cuJob.state is None:
            raise pywbem.CIMError(pywbem.CIM_ERR_NOT_FOUND, model['InstanceID'])
        jobState = cuJob.state
        if jobState == 'Applying':
            jobState = 'Running'
        jobState = getattr(self.Values.JobState, jobState,
            self.Values.JobState.Exception)

        if jobState == self.Values.JobState.Completed:
            self.produceResults(env, model, cuJob)

        created = utils.Time.format(cuJob.created)
        updated = utils.Time.format(cuJob.updated)
        # 2 hours before removing the job
        removalTime = utils.Time.format(cuJob.updated + 3600 * 2)

        #model['Caption'] = '' # TODO 
        #model['CommunicationStatus'] = self.Values.CommunicationStatus.<VAL> # TODO 
        model['DeleteOnCompletion'] = False
        #model['Description'] = '' # TODO 
        #model['DetailedStatus'] = self.Values.DetailedStatus.<VAL> # TODO 
        #model['ElapsedTime'] = pywbem.CIMDateTime() # TODO 
        #model['ElementName'] = '' # TODO 
        #model['ErrorCode'] = pywbem.Uint16() # TODO 
        #model['ErrorDescription'] = '' # TODO 
        #model['Generation'] = pywbem.Uint64() # TODO 
        #model['HealthState'] = self.Values.HealthState.<VAL> # TODO 
        #model['InstallDate'] = pywbem.CIMDateTime() # TODO 
        model['JobRunTimes'] = pywbem.Uint32(1)
        model['JobState'] = jobState
        #model['JobStatus'] = '' # TODO 
        model['LocalOrUtcTime'] = self.Values.LocalOrUtcTime.UTC_Time
        model['Name'] = self.JobName
        #model['Notify'] = '' # TODO 
        #model['OperatingStatus'] = self.Values.OperatingStatus.<VAL> # TODO 
        #model['OperationalStatus'] = [self.Values.OperationalStatus.<VAL>,] # TODO 
        #model['OtherRecoveryAction'] = '' # TODO 
        #model['Owner'] = '' # TODO 
        #model['PercentComplete'] = pywbem.Uint16() # TODO 
        #model['PrimaryStatus'] = self.Values.PrimaryStatus.<VAL> # TODO 
        #model['Priority'] = pywbem.Uint32() # TODO 
        #model['RecoveryAction'] = self.Values.RecoveryAction.<VAL> # TODO 
        #model['RunDay'] = pywbem.Sint8() # TODO 
        #model['RunDayOfWeek'] = self.Values.RunDayOfWeek.<VAL> # TODO 
        #model['RunMonth'] = self.Values.RunMonth.<VAL> # TODO 
        #model['RunStartInterval'] = pywbem.CIMDateTime() # TODO 
        #model['ScheduledStartTime'] = pywbem.CIMDateTime() # TODO 
        #model['StartTime'] = pywbem.CIMDateTime() # TODO 
        #model['Status'] = self.Values.Status.<VAL> # TODO 
        #model['StatusDescriptions'] = ['',] # TODO 
        model['TimeBeforeRemoval'] = pywbem.CIMDateTime(removalTime)
        model['TimeOfLastStateChange'] = pywbem.CIMDateTime(updated)
        model['TimeSubmitted'] = pywbem.CIMDateTime(created)
        #model['UntilTime'] = pywbem.CIMDateTime() # TODO 
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

        for job in self._task.list():
            model['InstanceID'] = self.createInstanceID(job.keyId)
            if keys_only:
                yield model
            else:
                try:
                    yield self.get_instance(env, model)
                except pywbem.CIMError, (num, msg):
                    if num not in (pywbem.CIM_ERR_NOT_FOUND, 
                                   pywbem.CIM_ERR_ACCESS_DENIED):
                        raise

    def cim_method_geterror(self, env, object_name):
        """Implements RPATH_UpdateConcreteJob.GetError()

        When the job is executing or has terminated without error, then
        this method returns no CIM_Error instance. However, if the job has
        failed because of some internal problem or because the job has
        been terminated by a client, then a CIM_Error instance is
        returned.
        
        Keyword arguments:
        env -- Provider Environment (pycimmb.ProviderEnvironment)
        object_name -- A pywbem.CIMInstanceName or pywbem.CIMCLassName 
            specifying the object on which the method GetError() 
            should be invoked.

        Returns a two-tuple containing the return value (type pywbem.Uint32 self.Values.GetError)
        and a list of CIMParameter objects representing the output parameters

        Output parameters:
        Error -- (type pywbem.CIMInstance(classname='CIM_Error', ...)) 
            If the OperationalStatus on the Job is not "OK", then this
            method will return a CIM Error instance. Otherwise, when the
            Job is "OK", null is returned.
            

        Possible Errors:
        CIM_ERR_ACCESS_DENIED
        CIM_ERR_INVALID_PARAMETER (including missing, duplicate, 
            unrecognized or otherwise incorrect parameters)
        CIM_ERR_NOT_FOUND (the target CIM Class or instance does not 
            exist in the specified namespace)
        CIM_ERR_METHOD_NOT_AVAILABLE (the CIM Server is unable to honor 
            the invocation request)
        CIM_ERR_FAILED (some other unspecified error occurred)

        """

        logger = env.get_logger()
        logger.log_debug('Entering %s.cim_method_geterror()' \
                % self.__class__.__name__)

        key = object_name.keybindings.get('InstanceID')
        if not key:
            rval = self.Values.GetError.Success
            return (rval, [])

        key = self.fromInstanceID(key)
        task = self._task.load(key)
        cuJob = task.job
        if not cuJob.created or cuJob.state != "Exception":
            rval = self.Values.GetError.Success
            return (rval, [])

        if cuJob.content is None:
            # No exception data
            rval = self.Values.GetError.Unspecified_Error
            return (rval, [])

        properties = dict(Message = cuJob.content,
# XXX FIXME: for some reason, passing the value as uint32 breaks the CIMOM
#            CIMStatusCode = pywbem.CIMProperty(name = 'CIMStatusCode',
#                                               value =  '1',
#                                               type = 'uint32'),
        )
        qualifiers = dict(
            Indication = pywbem.CIMQualifier('Indication', 'True',
                type = "boolean"),
            Exception = pywbem.CIMQualifier('Exception', 'True',
                type = "boolean"),
            EmbeddedInstance = pywbem.CIMQualifier('EmbeddedInstance', 'True',
                type = "boolean"),
        )

        className = 'CIM_Error'
        err = pywbem.CIMInstance(classname = className,
            properties = properties,
            path = pywbem.CIMInstanceName(classname = className,
                                          namespace = 'root/interop'),
            )

        out_params = []
        out_params.append(pywbem.CIMParameter('Error', type='instance',
                          value=err, qualifiers = qualifiers))

        rval = self.Values.GetError.Success
        return (rval, out_params)

    def produceResults(self, env, model, job):
        if job.content is None:
            return
        method = getattr(self, 'produceResult', None)
        if method is None:
            return
        results = []
        for line in job.content.split('\n'):
            inst = method(env, job, line.strip())
            if inst is None:
                continue
            results.append(inst)
        model['JobResults'] =  pywbem.CIMProperty('JobResults',
            results)

    @classmethod
    def createInstanceID(cls, resourceId):
        return 'com.rpath:jobs/%s' % resourceId

    @classmethod
    def fromInstanceID(cls, instanceID):
        qualified = instanceID.split(':', 1)[-1]
        return qualified.split('/', 1)[-1]
