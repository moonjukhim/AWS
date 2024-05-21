from __future__ import print_function
import boto3
import os, json
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

############################################################
import logging
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()
############################################################


dynamodb = boto3.resource('dynamodb')


def extractParams(event):
    UserId = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    NoteId = event["pathParameters"]["id"]
    dbName = os.environ['TABLE_NAME']
    
    return {
        'UserId': UserId,
        'NoteId': NoteId,
        'dbName': dbName
    }


def add_annotation(UserId, NoteId):
    print('Adding annotation...')
    xray_recorder.begin_subsegment('Delete a note')
    xray_recorder.put_annotation("UserId", UserId)
    xray_recorder.put_annotation("NoteId", NoteId)
    xray_recorder.end_subsegment()


def deleteNote(params):
    table = dynamodb.Table(params['dbName'])

    # DynamoDB 'delete_item' to delete a note
    table.delete_item(
        Key={
            'UserId': params['UserId'],
            'NoteId': int(params['NoteId'])
        }
    )


def lambda_handler(event, context):

    # Log debug information
    print(event)

    # create the response object, the error code is 500 unless manually set to a success
    response = {
        'isBase64Encoded': False,
        'statusCode': 500,
        'body': '',
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    try:
        # Extracting the user parameters from the event and environment
        params = extractParams(event)

        # Add X-Ray annotations to the trace
        add_annotation(params['UserId'], params['NoteId'])

        # Delete the note
        deleteNote(params)

    except Exception as e:
        print(e)
        response['body'] = e
        return response

    response['statusCode'] = 200
    response['body'] = str(params['NoteId'])
    return response
