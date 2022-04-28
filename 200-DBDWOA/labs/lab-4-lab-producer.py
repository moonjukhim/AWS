import boto3
import time
from random import randint

firehoseClient = boto3.client("firehose")

# Wait until delivery stream is available
while True:
    response = firehoseClient.list_delivery_streams()
    if len(response["DeliveryStreamNames"]) > 0:
        break
    print("No stream found, sleeping")
    time.sleep(30)

stream_name = response["DeliveryStreamNames"][0]

# Wait until the stream is ACTIVE
while True:
    response = firehoseClient.describe_delivery_stream(DeliveryStreamName=stream_name)
    if response["DeliveryStreamDescription"]["DeliveryStreamStatus"] == "ACTIVE":
        break
    time.sleep(30)

# Send data: record_time, user_id, game_id, score
while True:
    records = []
    record_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    for _ in range(0, randint(1, 10)):
        user_id = randint(0, 1000)
        game_id = randint(0, 20)
        score = randint(0, 10000)
        line = f"{record_time},{user_id},{game_id},{score}\n"
        records.append({"Data": line})

    # Send data
    print("Sending records: ", len(records))
    response = firehoseClient.put_record_batch(DeliveryStreamName=stream_name, Records=records)
    time.sleep(5)