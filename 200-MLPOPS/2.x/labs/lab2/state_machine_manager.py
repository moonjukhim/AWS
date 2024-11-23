import boto3
import sagemaker
import time
import random
import uuid
import logging
import stepfunctions
import io
import random
import json
import sys

from sagemaker.amazon.amazon_estimator import get_image_uri
from stepfunctions import steps
from stepfunctions.steps import TrainingStep, ModelStep, TransformStep
from stepfunctions.inputs import ExecutionInput
from stepfunctions.workflow import Workflow
from stepfunctions.template import TrainingPipeline
from stepfunctions.template.utils import replace_parameters_with_jsonpath

stepfunctions.set_stream_logger(level=logging.INFO)

region = boto3.Session().region_name

# Create a schema for input
event_input = ExecutionInput(schema={
    'BuildId': str,
    'Job': str,
    'Model': str,
    'Endpoint': str,
    'ECRArn': str,
    'DataBucketPath': str,
    'AuthorDate': str,
    'TriggerSource': str,
    'CommitId': str,
})

# Define static variables determined by appsec
sagemaker_role = 'arn:aws:iam::[ACCOUNT_ID]:role/LabVPC-notebook-role'
workflow_role = 'arn:aws:iam::[ACCOUNT_ID]:role/LabStack-2ff18e01-e448-468f-bff5--StepFunctionsRole-t6XCU8SCx8aI'
ecr_Arn = 'latest'
state_machine_arn = 'arn:aws:states:us-west-2:[ACCOUNT_ID]:stateMachine:TrainingStateMachine-zDlzvWHwimtJ'
state_machine_name = 'TrainingStateMachine-zDlzvWHwimtJ'
endpoint_wait_lambda = 'arn:aws:lambda:us-west-2:[ACCOUNT_ID]:function:LabStack-2ff18e01-e448-468f-bff-EndpointWaitLambda-3gXwBvzJUYaR'
model_test_step = 'arn:aws:lambda:us-west-2:[ACCOUNT_ID]:function:LabStack-2ff18e01-e448-468f-bff5-9-ModelTestLambda-u02tDDA9NiC2'
model_artifact_bucket = 's3://modelartifactbucket-us-west-2-6818271477398155/'
kms_key = 'a905e97f-cade-4a9c-b37a-0b2ac04b566b'

# Create a retry configuration for SageMaker throttling exceptions. This is attached to
# the SageMaker steps to ensure they are retried until they run.
SageMaker_throttling_retry = stepfunctions.steps.states.Retry(
    error_equals=['ThrottlingException', 'SageMaker.AmazonSageMakerException'],
    interval_seconds=5,
    max_attempts=60,
    backoff_rate=1.25
)

# Create an estimator with training specifications
custom_estimator = sagemaker.estimator.Estimator(
    ecr_Arn,
    sagemaker_role,
    train_instance_count = 1,
    train_instance_type = 'ml.m5.large',
    train_volume_size = 10,
    output_path=model_artifact_bucket,
    volume_kms_key=kms_key,
    max_run=300
)

# Create a step to train the model
training_step = steps.TrainingStep(
    'Train',
    estimator=custom_estimator,
    data={
        'training': sagemaker.inputs.TrainingInput(event_input['DataBucketPath'], content_type='csv')
    },
    job_name=event_input['Job'],
    result_path='$.train_step_result'
)
# Add a retry configuration to the training_step
training_step.add_retry(SageMaker_throttling_retry)

# Create a step to create the model
model_step = steps.ModelStep(
    'Create model',
    model=training_step.get_expected_model(),
    model_name=event_input['Model'],
    result_path='$.create_step_result'
)
# Add a retry configuration to the model_step
model_step.add_retry(SageMaker_throttling_retry)

# Create a step to generate an Amazon SageMaker endpoint configuration
endpoint_config_step = steps.EndpointConfigStep(
    "Create endpoint configuration",
    endpoint_config_name=event_input['Model'],
    model_name=event_input['Model'],
    initial_instance_count=1,
    instance_type='ml.m5.large',
    result_path='$.endpoint_config_step_result'
)
# Add a retry configuration to the endpoint_config_step
endpoint_config_step.add_retry(SageMaker_throttling_retry)

# Create a step to generate an Amazon SageMaker endpoint
endpoint_step = steps.EndpointStep(
    "Create endpoint",
    endpoint_name=event_input['Endpoint'],
    endpoint_config_name=event_input['Model'],
    result_path='$.endpoint_step_result'
)
# Add a retry configuration to the endpoint_step
endpoint_step.add_retry(SageMaker_throttling_retry)

# Chain the steps together to generate a full AWS Step Function
workflow_definition = steps.Chain([
    training_step,
    model_step,
    endpoint_config_step,
    endpoint_step
])

# Create an AWS Step Functions workflow based on inputs
workflow = Workflow(
    name=state_machine_name,
    state_machine_arn=state_machine_arn,
    definition=workflow_definition,
    role=workflow_role,
    execution_input=event_input
)

# Manually update some settings that are not generated correctly by the AWS Step Functions Data Science SDK
# https://aws-step-functions-data-science-sdk.readthedocs.io/en/stable/
jsonDef = workflow.definition.to_json(pretty=True)
jsonDef = jsonDef.replace("TrainingImage\": \"latest", "TrainingImage.$\": \"$$.Execution.Input['ECRArn']")
jsonDef = jsonDef.replace("Image\": \"latest", "Image.$\": \"$$.Execution.Input['ECRArn']")
jsonDef = jsonDef.replace("ModelDataUrl.$\": \"$['ModelArtifacts']['S3ModelArtifacts']", "ModelDataUrl.$\": \"$['train_step_result']['ModelArtifacts']['S3ModelArtifacts']")

# Print the AWS Step Function definition to the log
print(state_machine_arn)
print('---------')
print(jsonDef)
print('---------')
client = boto3.client('stepfunctions')

# Update the AWS Step Function using Boto3
try:
    response = client.update_state_machine(
            stateMachineArn=state_machine_arn,
            definition=jsonDef,
        )
    print(response)
except:
    e = sys.exc_info()[0]
    f = sys.exc_info()[1]
    g = sys.exc_info()[2]
    print("error (read error): "+str(e) + str(f) + str(g))

# Update the AWS Step Function using the AWS Step Functions Data Science SDK
# This does not work because of the 3 manual replacements made above for our use case
# workflow.update(workflow.definition, workflow_role)