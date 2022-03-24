# SQS, SNS

## 과제1: 개발 환경에 연결

## 과제2: 애플리케이션 개발

sns_publisher.py

```python
def publish_email(sns, topic_arn, email_mesg, email_subj):
    print(
        "\nRUNNING SOLUTION CODE:",
        "publish_email!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    topic = sns.Topic(topic_arn)
    topic.publish(Message=email_mesg, Subject=email_subj)

def publish_order(sns, topic_arn, json_order):
    print(
        "\nRUNNING SOLUTION CODE:",
        "publish_order!",
        "Follow the steps in the lab guide to replace this method with your own implementation.")
    topic = sns.Topic(topic_arn)
    topic.publish(Message=json_order)
```

### 2.3: SQS Consumer 개발

sqs_consumer.py

```python
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
```