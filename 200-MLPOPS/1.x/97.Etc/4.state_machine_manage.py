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
from datetime import datetime, timedelta

from sagemaker.amazon.amazon_estimator import get_image_uri
from stepfunctions import steps
from stepfunctions.steps import TrainingStep, ModelStep, TransformStep
from stepfunctions.inputs import ExecutionInput
from stepfunctions.workflow import Workflow
from stepfunctions.template import TrainingPipeline
from stepfunctions.template.utils import replace_parameters_with_jsonpath

stepfunctions.set_stream_logger(level=logging.INFO)

region = boto3.Session().region_name

model_namea = f"DEMO-decission-tree-pred-{datetime.now():%Y-%m-%d-%H-%M-%S}"
model_nameb = f"DEMO-random-forest-pred-{datetime.now():%Y-%m-%d-%H-%M-%S}"

# Create a schema for input
event_input = ExecutionInput(schema={
    'BuildId': str,
    'ModelA': str,
    'ModelB': str,
    'Endpoint': str,
    'ecrArnA': str,
    'ecrArnB': str,
    'dataBucketPath': str,
    'authorDate': str,
    'triggerSource': str,
    'commitId': str,
})

# Define static variables determined by appsec
sagemaker_role = 'arn:aws:iam::860660749434:role/qls-28583-e80f1ff13e6e273a-SageMakerRole-ND1XCTEJG4JM'
workflow_role = 'arn:aws:iam::860660749434:role/qls-28583-e80f1ff13e6e273a-StepFunctionsRole-1873OQ5BK2E8U'
ecr_ArnA = 'latesta'
ecr_ArnB = 'latestb'
state_machine_arn = 'arn:aws:states:us-west-2:860660749434:stateMachine:trainingStateMachine-qxyULJR6C733'
state_machine_name = 'trainingStateMachine-qxyULJR6C733'
dynamoDBTable = 'qls-28583-e80f1ff13e6e273a-DynamoDBTable-13I0WGPSJZZVI'
endpoint_wait_lambda = 'arn:aws:lambda:us-west-2:860660749434:function:qls-28583-e80f1ff13e6e273a-endpointWaitLambda-dpyAW80Wkrh3'
model_test_step = 'arn:aws:lambda:us-west-2:860660749434:function:qls-28583-e80f1ff13e6e273a-modelTestLambda-epON4fjleM4T'
multivariant_test_step = 'arn:aws:lambda:us-west-2:860660749434:function:qls-28583-e80f1ff13e6e273a-multiVariantTestLambda-tJUkM21sUgu1'
endpoint_create_lambda = 'arn:aws:lambda:us-west-2:860660749434:function:qls-28583-e80f1ff13e6e273a-createEndpointLambda-04m4ezKdSKAq'
destination_capture_bucket = 's3://qls-28583-e80f1ff13e6e273a-modelartifactbucket-hysxcdr5gqtn/capturedata/'
model_bucketA = 's3://qls-28583-e80f1ff13e6e273a-modelartifactbucket-hysxcdr5gqtn/modelA/'
model_bucketB = 's3://qls-28583-e80f1ff13e6e273a-modelartifactbucket-hysxcdr5gqtn/modelB/'
kms_key = '48e16394-63f9-45fa-afb3-b34d87c76b0e'

endpoint_name = f"DEMO-iris-pred-{datetime.now():%Y-%m-%d-%H-%M-%S}"

####START MODEL A CONFIGURATION###########

# Create a retry configuration for SageMaker throttling exceptions. This is attached to
# the SageMaker steps to ensure they are retried until they run.
SageMaker_throttling_retry = stepfunctions.steps.states.Retry(
    error_equals=['ThrottlingException', 'SageMaker.AmazonSageMakerException'],
    interval_seconds=5,
    max_attempts=60,
    backoff_rate=1.25
)

# Create an estimator with training specifications for modelA
custom_estimatorA = sagemaker.estimator.Estimator(
    ecr_ArnA,
    role = sagemaker_role,
    train_instance_count = 1,
    train_instance_type = 'ml.m5.xlarge',
    train_volume_size = 10,
    output_path=model_bucketA,
    volume_kms_key=kms_key
)
# Create a step to train for modelA
training_stepA = steps.TrainingStep(
    'Train ModelA',
    estimator=custom_estimatorA,
    data={
        'training': sagemaker.inputs.TrainingInput(event_input['dataBucketPath'], content_type='csv')
    },
    job_name="States.Format('JobA-{}', $$.Execution.Input['BuildId'])",
    result_path='$.train_step_result'
)
# Add a retry configuration to the training_step
training_stepA.add_retry(SageMaker_throttling_retry)

# Create a step to save the modelA
model_stepA = steps.ModelStep(
    'Create ModelA',
    model=training_stepA.get_expected_model(),
    model_name=event_input['ModelA'],
    result_path='$.save_step_result'
)
# Add a retry configuration to the model_step
model_stepA.add_retry(SageMaker_throttling_retry)

# Create a step to input model data into the model artifact store in DynamoDB
register_artifact_step_a = steps.service.DynamoDBPutItemStep(
    "Insert ModelA data into registry",
    parameters={
            "Item": {
                "RunId": {
                    "S": event_input['ModelA']
                },
                "authorDate": {
                    "S": event_input['authorDate']
                },
                "commitId": {
                    "S": event_input['commitId']
                },
                "JobId": {
                    "S.$": "States.Format('JobA-{}', $$.Execution.Input['BuildId'])"
                },
                "dataBucketPath": {
                    "S": event_input['dataBucketPath']
                },
                "ecrImageTag": {
                    "S": event_input['BuildId']
                },
                "endpointName": {
                    "S": event_input['Endpoint']
                },
                "triggerSource": {
                    "S": event_input['triggerSource']
                },
                "Accuracy": {
                    "N": "0"
                }
            },
            "TableName": dynamoDBTable
        },
        result_path='$.record_artifact_step_result_a'
)

####END MODEL A CONFIGURATION###########

####START MODEL B CONFIGURATION###########
# Create an estimator with training specifications for modelB
custom_estimatorB = sagemaker.estimator.Estimator(
    ecr_ArnB,
    role = sagemaker_role,
    train_instance_count = 1,
    train_instance_type = 'ml.m5.xlarge',
    train_volume_size = 10,
    output_path=model_bucketB,
    volume_kms_key=kms_key
)
# Create a step to train for modelB
training_stepB = steps.TrainingStep(
    'Train ModelB',
    estimator=custom_estimatorB,
    data={
        'training': sagemaker.inputs.TrainingInput(event_input['dataBucketPath'], content_type='csv')
    },
    job_name="States.Format('JobB-{}', $$.Execution.Input['BuildId'])",
    result_path='$.train_step_result'
)
# Add a retry configuration to the training_step
training_stepB.add_retry(SageMaker_throttling_retry)

# Create a step to save the modelB
model_stepB = steps.ModelStep(
    'Create ModelB',
    model=training_stepB.get_expected_model(),
    model_name=event_input['ModelB'],
    result_path='$.save_step_result'
)
# Add a retry configuration to the model_step
model_stepB.add_retry(SageMaker_throttling_retry)

# Create a step to input model data into the model artifact store in DynamoDB
register_artifact_step_b = steps.service.DynamoDBPutItemStep(
    "Insert ModelB data into registry",
    parameters={
            "Item": {
                "RunId": {
                    "S": event_input['ModelB']
                },
                "authorDate": {
                    "S": event_input['authorDate']
                },
                "commitId": {
                    "S": event_input['commitId']
                },
                "JobId": {
                    "S.$": "States.Format('JobB-{}', $$.Execution.Input['BuildId'])"
                },
                "dataBucketPath": {
                    "S": event_input['dataBucketPath']
                },
                "ecrImageTag": {
                    "S": event_input['BuildId']
                },
                "endpointName": {
                    "S": event_input['Endpoint']
                },
                "triggerSource": {
                    "S": event_input['triggerSource']
                },
                "Accuracy": {
                    "N": "0"
                }
            },
            "TableName": dynamoDBTable
        },
        result_path='$.record_artifact_step_result_b'
)



####END MODEL B CONFIGURATION###########

####START CREATE ENDPOINT ###########

# Create a step to generate an Amazon SageMaker endpoint configuration


# Create Endpoint using Lambda

endpoint_create_step = steps.LambdaStep(
    "Create multi-variant endpoint",
    parameters={
        "FunctionName": endpoint_create_lambda,
        "Payload":{
            "Input.$":"$"
        }
    }
)
endpoint_create_step.add_retry(SageMaker_throttling_retry)


####END CREATE ENDPOINT ###########

# Create a step that triggers an AWS Lambda function that tests if the endpoint is InService
endpoint_wait_step = steps.LambdaStep(
    "Test endpoint in service",
    parameters={
        "FunctionName": endpoint_wait_lambda,
        "Payload":{
            "Input.$":"$"
        }
    },
    result_path='$.endpoint_wait_step_result'
)
# Create a retry configuration for the endpoint_wait_step
endpoint_wait_step_retry = stepfunctions.steps.states.Retry(
    error_equals=['NotInService'],
    interval_seconds=15,
    max_attempts=30,
    backoff_rate=1.25
)
# Add a retry configuration to the endpoint_wait_step
endpoint_wait_step.add_retry(endpoint_wait_step_retry)


####START MODEL TEST ACCURACY ###########

# Create a step that invokes an AWS Lambda function to test multi model accuracy 
# update the artifact store to reflect the accuracy for both variant of the models
model_test_step = steps.LambdaStep(
    "Test model",
    parameters={
        "FunctionName": multivariant_test_step,
        "Payload":{
            "Input.$":"$"
        }
    },
    result_path='$.model_test_step_result'
)
### END MODEL TEST ACCURACY ####

### START WORK FLOW DEFINITION ####

train_step_A = steps.Chain([
    training_stepA,
    model_stepA,
    register_artifact_step_a
    ])
train_step_B = steps.Chain([
    training_stepB,
    model_stepB,
    register_artifact_step_b
    ])

training_step = stepfunctions.steps.states.Parallel("Customer Estimators")
training_step.add_branch(train_step_A)
training_step.add_branch(train_step_B)

# Chain the steps together to generate a full AWS Step Functions
workflow_definition = steps.Chain([
    training_step,
    endpoint_create_step,
    endpoint_wait_step,
    model_test_step
])

# Create a Amazon Step Function workflow based in inputs
workflow = Workflow(
    name=state_machine_name,
    state_machine_arn=state_machine_arn,
    definition=workflow_definition,
    role=workflow_role,
    execution_input=event_input
)

### END WORK FLOW DEFINITION ####

# Manually update some settings that are not generated correctly by the AWS Step Functions Data Science SDK.
jsonDef = workflow.definition.to_json(pretty=True)
jsonDef = jsonDef.replace("TrainingImage\": \"latesta", "TrainingImage.$\": \"$$.Execution.Input['ecrArnA']")
jsonDef = jsonDef.replace("TrainingImage\": \"latestb", "TrainingImage.$\": \"$$.Execution.Input['ecrArnB']")
jsonDef = jsonDef.replace("Image\": \"latesta", "Image.$\": \"$$.Execution.Input['ecrArnA']")
jsonDef = jsonDef.replace("Image\": \"latestb", "Image.$\": \"$$.Execution.Input['ecrArnB']")
jsonDef = jsonDef.replace("ModelDataUrl.$\": \"$['ModelArtifacts']['S3ModelArtifacts']", "ModelDataUrl.$\": \"$['train_step_result']['ModelArtifacts']['S3ModelArtifacts']")
jsonDef = jsonDef.replace("TrainingJobName", "TrainingJobName.$")

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