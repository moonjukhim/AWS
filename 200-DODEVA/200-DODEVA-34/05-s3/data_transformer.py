# Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights
# reserved.

import boto3
import sys
import csv
import json
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
import utils as s3setup
import solution as s3solution

# TODO 1: Set input bucket name (must be globally unique)
INPUT_BUCKET_NAME = "<globally-unique-input-bucket-name>"

# TODO 2: Set output bucket name (must be globally unique)
OUTPUT_BUCKET_NAME = "<globally-unique-output-bucket-name>"


class DataTransformer:

    s3 = None
    bucketSource = None
    bucketDest = None

    def __init__(self):
        self.INPUT_BUCKET_NAME = INPUT_BUCKET_NAME
        self.OUTPUT_BUCKET_NAME = OUTPUT_BUCKET_NAME

        # Set the region in which the lab is running
        self.LAB_REGION = boto3.session.Session().region_name

        # Create S3 resource
        self.s3 = self.create_s3_resource()

        # Set up the input bucket and copy the CSV files. Also, set up the
        # output bucket
        self.bucketSource = s3setup.setup(inputbucket=self.INPUT_BUCKET_NAME,
                                          outputbucket=self.OUTPUT_BUCKET_NAME,
                                          region=self.LAB_REGION)

        inputbucket = self.s3.Bucket(self.INPUT_BUCKET_NAME)
        outputbucket = self.s3.Bucket(self.OUTPUT_BUCKET_NAME)

        # Get summary information for all objects in input bucket
        # Iterate over the list of object summaries
        for object_summary in inputbucket .objects.all():
            # Get the object key from each object summary
            csvkey = object_summary.key

            # Retrieve the object with the specified key from the input bucket
            self.download_file_from_bucket(inputbucket, csvkey)

            # Convert the file from CSV to JSON format
            jsonkey = self.transform(csvkey)

            # TODO 7: Switch to enhanced file upload
            # Put the transformed file into the output bucket
            self.upload_file_to_bucket(jsonkey, outputbucket, jsonkey)
            # self.upload_file_to_bucket_enhanced(jsonkey, outputbucket, jsonkey)

            # Generate a pre-signed URL for the JSON file
            url = self.generate_presigned_url(self.OUTPUT_BUCKET_NAME, jsonkey)
            print("Pre-signed URL: " + url)

    def transform(self, file):
        print('DataTransformer: Transforming file: ' + file)
        f = open(file, 'r')

        # Get the headings
        fn = f.readlines(1)[0].split(',')

        reader = csv.DictReader(f, fieldnames=fn)
        # Convert to JSON
        out = json.dumps([row for row in reader])
        f.close()
        print(file)

        # Store the JSON in a file
        name = file.split('.')[0]
        key = file.split('.')[0] + ".json"

        name = key
        f = open(name, 'w+')
        f.write(out)
        f.close()
        print('DataTransformer: Done')
        return name

    def create_s3_resource(self):
        """Return a S3 resource object."""

        # TODO 3: Replace the solution with your own code
        return s3solution.create_s3_resource()

    def download_file_from_bucket(self, bucket, key):
        """Download a file from a S3 bucket

        Keyword arguments:
        bucket -- S3 bucket from which object must be retrieved
        key -- Key (path & filename) of the object to be retrieved
        """

        # TODO 4: Replace the solution with your own code
        s3solution.download_file_from_bucket(bucket, key)

    def upload_file_to_bucket(self, filename, bucket, key):
        """Upload a file to a S3 bucket

        Keyword arguments:
        filename -- Path of file to be uploaded to bucket
        bucket -- S3 bucket to which file must be uploaded
        key -- Key (path & filename) of the new uploaded object in the bucket
        """

        # TODO 5: Replace the solution with your own code
        s3solution.upload_file_to_bucket(filename, bucket, key)

    def generate_presigned_url(self, bucketname, key):
        """Return a presigned URL to a file

        Keyword arguments:
        bucket -- S3 bucket where the file exists
        key -- Key (path & filename) of the file
        """
        s3 = self.s3
        # TODO 6: Replace the solution with your own code
        return s3solution.generate_presigned_url(self.s3, bucketname, key)

    def upload_file_to_bucket_enhanced(self, filename, bucket, key):
        """Upload a file to a S3 bucket using AES 256 server-side encryption

        Keyword arguments:
        filename -- Path of file to be uploaded to bucket
        bucket -- S3 bucket to which file must be uploaded
        key -- Key (path & filename) of the new uploaded object in the bucket
        """

        # TODO 8: Replace the solution with your own code
        s3solution.upload_file_to_bucket_enhanced(filename, bucket, key)

if __name__ == '__main__':
    DataTransformer()
