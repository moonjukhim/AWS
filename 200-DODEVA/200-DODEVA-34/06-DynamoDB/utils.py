# Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights
# reserved.

import boto3
import botocore
from botocore.exceptions import NoCredentialsError, ClientError, EndpointConnectionError

# 'EU'|'eu-west-1'|'us-west-1'|'us-west-2'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'sa-east-1'|'cn-north-1'|'eu-central-1'
LAB_S3_BUCKET_NAME = "aws-tc-largeobjects"
LAB_S3_BUCKET_REGION = "us-west-2"
LAB_S3_RESERVATIONS_DATA_FILE_KEY = "AWS-100-DEV/v3.1/binaries/input/lab-3-dynamoDB/ReservationsData.csv"
LAB_S3_CUSTOMER_REPORT_PREFIX = "AWS-100-DEV/v3.1/binaries/input/lab-3-dynamoDB/CustomerRecord"
LAB_S3_FILE_KEY = "ReservationsData.csv"
LAB_S3_RESERVATIONS_TABLE_NAME = "Reservations"


def is_table_active(tableName=LAB_S3_RESERVATIONS_TABLE_NAME):
    # Check if the given table exists and active
    try:
        resource = boto3.resource('dynamodb')
        table = resource.Table(tableName)
        if table.table_status == 'ACTIVE':
            return True
    except ClientError as err:
        if (err.response.get('Error').get('Code')
                == 'ResourceNotFoundException'):
            print("{0} Table not found".format(tableName))
    except Exception as err:
        print("Error message: {0}".format(err))
    return False
