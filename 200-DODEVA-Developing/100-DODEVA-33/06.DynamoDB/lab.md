# DynamoDB

## 과제1: 개발 환경에 연결

## 과제2: 애플리케이션 개발

### 과제2.1: 테이블 및 글로벌 보조 인덱스 생성

```python
 # Create a DynamoDB table with the parameters provided

    table = dynamodb.create_table(TableName=table_name,
                                    KeySchema=key_schema,
                                    AttributeDefinitions=attribute_definitions,
                                    ProvisionedThroughput=provisioned_throughput,
                                    GlobalSecondaryIndexes=global_secondary_indexes,
                                    )
```

### 과제2.2: 테이블에 데이터 업로드

```python
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
```

### 과제2.3: 쿼리 실행

```python
 dynamodb = boto3.resource('dynamodb')
        recs = query_city_related_items(
            dynamodb, RESERVATIONS_TABLE_NAME, CITY_DATE_INDEX_NAME, city)

        # Retrieves and prints from recs dictionary returned by the query.
        for rec in recs['Items']:
            print("\t", rec['CustomerId'], rec['Date'])
        count_for_city = len(recs['Items'])
        print("Count of Reservations in the city: {0}".format(count_for_city))
```

### 과제2.4: 데이터 업데이트


