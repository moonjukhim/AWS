# Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights
# reserved.

import boto3
import sys


def create_s3_resource():
    print(
        "\nRUNNING SOLUTION CODE:",
        "create_s3_resource!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    s3 = boto3.resource('s3')
    return s3


def download_file_from_bucket(bucket, key):
    print(
        "\nRUNNING SOLUTION CODE:",
        "download_file_from_bucket!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    bucket.download_file(key, key)


def upload_file_to_bucket(filename, bucket, key):
    print(
        "\nRUNNING SOLUTION CODE:",
        "upload_file_to_bucket!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    bucket.upload_file(filename, key)


def generate_presigned_url(s3, bucketname, key):
    print(
        "\nRUNNING SOLUTION CODE:",
        "generate_presigned_url!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    url = s3.meta.client.generate_presigned_url(
        'get_object', Params={'Bucket': bucketname, 'Key': key}, ExpiresIn=900)
    return url


def upload_file_to_bucket_enhanced(filename, bucket, key):
    print(
        "\nRUNNING SOLUTION CODE:",
        "upload_file_to_bucket_enhanced!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    bucket.upload_file(
        filename, key, ExtraArgs={
            'ServerSideEncryption': 'AES256', 'Metadata': {
                'contact': 'John Doe'}})
