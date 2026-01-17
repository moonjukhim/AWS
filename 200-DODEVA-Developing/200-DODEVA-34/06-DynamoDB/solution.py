# Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights
# reserved.

import boto3
import time
from boto3.dynamodb.conditions import Key


# Put an item in the reservations table using the attribute values for
# CustomerId, City, and Date attributes
def add_item_to_table(reservations_table, customer_id, city, date):
    print(
        "\nRUNNING SOLUTION CODE:",
        "put_item_in_table!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")

    reservations_table.put_item(
        Item={
            'CustomerId': customer_id,
            'City': city,
            'Date': date})


# Query the table's global secondary index for items that contain the
# given city name
def query_city_related_items(dynamodb, reservations_table_name, gsi_name, city):
    print(
        "\nRUNNING SOLUTION CODE:",
        "query_city_related_items!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")

    reservations_table = dynamodb.Table(reservations_table_name)
    recs = reservations_table.query(
        IndexName=gsi_name,
        KeyConditionExpression=Key('City').eq(city)
    )

    return recs


def update_item_with_link(
        dynamodb,
        reservations_table_name,
        customer_id,
        report_url):
    print(
        "\nRUNNING SOLUTION CODE:",
        "updateItemWithLink!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    myTable = dynamodb.Table(reservations_table_name)
    try:
        # Update item in table for the given customer_id key.
        resp = myTable.update_item(
            Key={'CustomerId': str(customer_id)},
            UpdateExpression='set CustomerReportUrl=:val1',
            ExpressionAttributeValues={':val1': report_url})
        print("Item updated")
        print(
            "CustomerId:{0}, CustomerReportUrl:{1}".format(
                customer_id,
                report_url))
    except Exception as err:
        print("Error message {0}".format(err))
