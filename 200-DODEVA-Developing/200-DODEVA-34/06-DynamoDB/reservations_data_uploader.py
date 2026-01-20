# Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights
# reserved.

import csv
import boto3
from botocore.exceptions import ClientError
import utils
import solution as dynamodb_solution

BUCKET_NAME = utils.LAB_S3_BUCKET_NAME
BUCKET_REGION = utils.LAB_S3_BUCKET_REGION
RESERVATIONS_DATA_FILE_KEY = utils.LAB_S3_RESERVATIONS_DATA_FILE_KEY
FILE_NAME = utils.LAB_S3_FILE_KEY
RESERVATIONS_TABLE_NAME = utils.LAB_S3_RESERVATIONS_TABLE_NAME
DELIMITER = ","


def load_reservations_data(
        tableName=RESERVATIONS_TABLE_NAME,
        bucketRegion=BUCKET_REGION,
        bucket=BUCKET_NAME,
        fKey=RESERVATIONS_DATA_FILE_KEY,
        FName=FILE_NAME):
    num_failures = 0
    try:
        # Create an S3 resource to download the reservations data file from the
        # S3 bucket
        S3 = boto3.resource('s3', bucketRegion)
        try:
            # Check if you have permissions to access the bucket and then
            # retrieve a reference to it
            S3.meta.client.head_bucket(Bucket=bucket)
            myBucket = S3.Bucket(bucket)
        except ClientError as err:
            print("Could not find bucket")
            print("Error message {0}".format(err))
            num_failures = 9999
            return num_failures
        except Exception as err:
            print("Error message {0}".format(err))
            num_failures = 9999
            return num_failures

        try:
            # Download the CSV-formatted reservations data file
            myBucket.download_file(fKey, FName)
        except Exception as err:
            print("Error message {0}".format(err))
            print("Failed to download the reservations data file from S3 bucket")
            num_failures = 9999
            return num_failures
        print("Reading reservations data from file, going to begin upload")
        with open(FName, newline='') as fh:
            reader = csv.DictReader(fh, delimiter=DELIMITER)
            # Create a DynamoDB resource
            dynamodb = boto3.resource('dynamodb')

            # Retrieve a reference to the Reservations table
            reservations_table = dynamodb.Table(RESERVATIONS_TABLE_NAME)

            # Add an item for each row in the file
            for row in reader:
                try:
                    add_item_to_table(
                        reservations_table,
                        row['CustomerId'],
                        row['City'],
                        row['Date'])
                except Exception as err:
                    print("Error message {0}".format(err))
                    num_failures += 1
            print("Upload completed.")
    except Exception as err:
        print("Failed to add item in {0}".format(tableName))
        print("Error message {0}".format(err))
        num_failures = 9999
    return num_failures


def add_item_to_table(reservations_table, customer_id, city, date):
    """Put an item in the reservations table using the attribute values in the row object

    Keyword arguments:
    reservations_table -- Table object
    customer_id -- Customer ID
    city -- City Name
    date -- Date
    """

    # TODO 1: Replace the solution with your own code
    dynamodb_solution.add_item_to_table(
        reservations_table, customer_id, city, date)

if __name__ == '__main__':
    print("Going to load data")
    load_reservations_data()
