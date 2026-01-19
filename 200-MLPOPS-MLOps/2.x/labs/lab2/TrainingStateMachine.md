```json
{
  "StartAt": "Train",
  "States": {
    "Train": {
      "ResultPath": "$.train_step_result",
      "Resource": "arn:aws:states:::sagemaker:createTrainingJob.sync",
      "Parameters": {
        "AlgorithmSpecification": {
          "TrainingImage.$": "$$.Execution.Input['ECRArn']",
          "TrainingInputMode": "File"
        },
        "OutputDataConfig": {
          "S3OutputPath": "s3://modelartifactbucket-us-west-2-4514084112578296/"
        },
        "StoppingCondition": {
          "MaxRuntimeInSeconds": 300
        },
        "ResourceConfig": {
          "InstanceCount": 1,
          "InstanceType": "ml.m5.large",
          "VolumeSizeInGB": 10,
          "VolumeKmsKeyId": "3381480e-f19a-4de2-9a6b-a792cfe7761a"
        },
        "RoleArn": "arn:aws:iam::593125668547:role/LabVPC-notebook-role",
        "InputDataConfig": [
          {
            "DataSource": {
              "S3DataSource": {
                "S3DataType": "S3Prefix",
                "S3Uri.$": "$$.Execution.Input['DataBucketPath']",
                "S3DataDistributionType": "FullyReplicated"
              }
            },
            "ContentType": "csv",
            "ChannelName": "training"
          }
        ],
        "TrainingJobName.$": "$$.Execution.Input['Job']"
      },
      "Type": "Task",
      "Next": "Create model",
      "Retry": [
        {
          "ErrorEquals": [
            "ThrottlingException",
            "SageMaker.AmazonSageMakerException"
          ],
          "IntervalSeconds": 5,
          "MaxAttempts": 60,
          "BackoffRate": 1.25
        }
      ]
    },
    "Create model": {
      "ResultPath": "$.create_step_result",
      "Parameters": {
        "ExecutionRoleArn": "arn:aws:iam::593125668547:role/LabVPC-notebook-role",
        "ModelName.$": "$$.Execution.Input['Model']",
        "PrimaryContainer": {
          "Environment": {},
          "Image.$": "$$.Execution.Input['ECRArn']",
          "ModelDataUrl.$": "$['train_step_result']['ModelArtifacts']['S3ModelArtifacts']"
        }
      },
      "Resource": "arn:aws:states:::sagemaker:createModel",
      "Type": "Task",
      "Next": "Create endpoint configuration",
      "Retry": [
        {
          "ErrorEquals": [
            "ThrottlingException",
            "SageMaker.AmazonSageMakerException"
          ],
          "IntervalSeconds": 5,
          "MaxAttempts": 60,
          "BackoffRate": 1.25
        }
      ]
    },
    "Create endpoint configuration": {
      "ResultPath": "$.endpoint_config_step_result",
      "Resource": "arn:aws:states:::sagemaker:createEndpointConfig",
      "Parameters": {
        "EndpointConfigName.$": "$$.Execution.Input['Model']",
        "ProductionVariants": [
          {
            "InitialInstanceCount": 1,
            "InstanceType": "ml.m5.large",
            "ModelName.$": "$$.Execution.Input['Model']",
            "VariantName": "AllTraffic"
          }
        ]
      },
      "Type": "Task",
      "Next": "Test if endpoint is in service",
      "Retry": [
        {
          "ErrorEquals": [
            "ThrottlingException",
            "SageMaker.AmazonSageMakerException"
          ],
          "IntervalSeconds": 5,
          "MaxAttempts": 60,
          "BackoffRate": 1.25
        }
      ]
    },
    "Test if endpoint is in service": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:us-west-2:593125668547:function:LabStack-2ff18e01-e448-468f-bff-EndpointWaitLambda-ksN7JSCZHNJZ:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "NotInService"
          ],
          "IntervalSeconds": 15,
          "MaxAttempts": 30,
          "BackoffRate": 1,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Test model",
      "ResultPath": "$.endpoint_wait_step_result"
    },
    "Test model": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:us-west-2:593125668547:function:LabStack-2ff18e01-e448-468f-bff5-9-ModelTestLambda-X5WSp1VeWkf2:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Create endpoint",
      "ResultPath": "$.model_test_step_result"
    },
    "Create endpoint": {
      "ResultPath": "$.endpoint_step_result",
      "Resource": "arn:aws:states:::sagemaker:createEndpoint",
      "Parameters": {
        "EndpointConfigName.$": "$$.Execution.Input['Model']",
        "EndpointName.$": "$$.Execution.Input['Endpoint']"
      },
      "Type": "Task",
      "End": true,
      "Retry": [
        {
          "ErrorEquals": [
            "ThrottlingException",
            "SageMaker.AmazonSageMakerException"
          ],
          "IntervalSeconds": 5,
          "MaxAttempts": 60,
          "BackoffRate": 1.25
        }
      ]
    }
  }
}
```