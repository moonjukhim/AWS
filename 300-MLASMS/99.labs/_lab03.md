1. EMR hdfs data

```bash
#!/bin/bash
#Add csv file to hdfs directory
s3-dist-cp --src=s3://labstack-2ff18e01-e448-468f-bff5-9d-labdatabucket-4ootfiq15ax6/scripts/data/ --dest=hdfs:///emrdata

#Load data from hdfs to external hive table
hive  <<-EOF1
    DROP TABLE IF EXISTS adult_data;
    CREATE EXTERNAL TABLE IF NOT EXISTS adult_data (
        age int,
        workclass string,
        fnlwgt int,
        education string,
        education_num int,
        marital_status string,
        occupation string,
        relationship string,
        race string,
        sex string,
        capital_gain int,
        capital_loss int,
        hours_per_week int,
        native_country string,
        income string
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde';
    LOAD DATA INPATH '/emrdata/adult_data.csv' OVERWRITE INTO TABLE adult_data;
EOF1

```