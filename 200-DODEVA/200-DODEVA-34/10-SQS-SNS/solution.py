# Copyright 2017 Amazon Web Services, Inc. or its affiliates. All rights
# reserved.

import utils
import json


def publish_email(sns, topic_arn, email_mesg, email_subj):
    print(
        "\nRUNNING SOLUTION CODE:",
        "publish_email!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    topic = sns.Topic(topic_arn)
    topic.publish(Message=email_mesg, Subject=email_subj)


def convert_order_to_json(porder):
    print(
        "\nRUNNING SOLUTION CODE:",
        "convert_order_to_json!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    json_order = json.dumps(porder, default=utils.jdefault, indent=4)
    return json_order


def publish_order(sns, topic_arn, json_order):
    print(
        "\nRUNNING SOLUTION CODE:",
        "publish_order!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    topic = sns.Topic(topic_arn)
    topic.publish(Message=json_order)


def get_sqs_queue(sqs, QUEUE_NAME):
    print(
        "\nRUNNING SOLUTION CODE:",
        "get_queue!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    return sqs.get_queue_by_name(QueueName=QUEUE_NAME)


def get_messages(queue):
    print(
        "\nRUNNING SOLUTION CODE:",
        "get_messages!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    return queue.receive_messages(
        AttributeNames=['All'],
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20)


def get_attributes(mesg):
    print(
        "\nRUNNING SOLUTION CODE:",
        "get_attributes!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    return mesg.attributes


def delete_message(mesg):
    print(
        "\nRUNNING SOLUTION CODE:",
        "delete_message!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    mesg.delete()
