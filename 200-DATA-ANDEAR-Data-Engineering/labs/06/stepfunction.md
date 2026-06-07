

```json
{
  "Comment": "An example of the Amazon States Language for running jobs on Amazon EMR",
  "StartAt": "Create an EMR cluster",
  "States": {
    "Create an EMR cluster": {
      "Type": "Task",
      "Resource": "arn:aws:states:::elasticmapreduce:createCluster.sync",
      "Parameters": {
        "Name": "labCluster",
        "VisibleToAllUsers": true,
        "ReleaseLabel": "emr-6.3.0",
        "Applications": [
          {
            "Name": "Spark"
          },
          {
            "Name": "Flink"
          },
          {
            "Name": "Livy"
          }
        ],
        "ServiceRole": "LabStack-2ff18e01-e448-468f-bff5-9d7-EMRDefaultRole-9erqdpMHSr1m",
        "JobFlowRole": "LabStack-2ff18e01-e448-468f-bff5-9d74a2cc4543-emwMCmDXhZbmHREBbpp2wR-0-EMREC2InstanceProfile-kKEORq86fmSX",
        "LogUri": "s3://databucket--9632183891563080/logs/",
        "Instances": {
          "Ec2SubnetId": "subnet-0118de91c58ef6ad7",
          "KeepJobFlowAliveWhenNoSteps": true,
          "InstanceFleets": [
            {
              "Name": "LeaderFleet",
              "InstanceFleetType": "MASTER",
              "TargetOnDemandCapacity": 1,
              "InstanceTypeConfigs": [
                {
                  "InstanceType": "m4.large"
                }
              ]
            },
            {
              "Name": "MyCoreFleet",
              "InstanceFleetType": "CORE",
              "TargetOnDemandCapacity": 2,
              "InstanceTypeConfigs": [
                {
                  "InstanceType": "m4.large"
                }
              ]
            }
          ]
        }
      },
      "ResultPath": "$.cluster",
      "Next": "Submit PySpark Job"
    },
    "Submit PySpark Job": {
      "Type": "Task",
      "Resource": "arn:aws:states:::elasticmapreduce:addStep.sync",
      "Parameters": {
        "ClusterId.$": "$.cluster.ClusterId",
        "Step": {
          "Name": "pyspark-job",
          "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
              "spark-submit",
              "--deploy-mode",
              "cluster",
              "--executor-memory",
              "1g",
              "s3://databucket--9632183891563080/scripts/script.py"
            ]
          }
        }
      },
      "ResultPath": "$.sparkJob",
      "Next": "Terminate the EMR cluster"
    },
    "Terminate the EMR cluster": {
      "Type": "Task",
      "Resource": "arn:aws:states:::elasticmapreduce:terminateCluster",
      "Parameters": {
        "ClusterId.$": "$.cluster.ClusterId"
      },
      "ResultPath": "$.terminateCluster",
      "Next": "Create Amazon Athena summarized table"
    },
    "Create Amazon Athena summarized table": {
      "Type": "Task",
      "Resource": "arn:aws:states:::athena:startQueryExecution.sync",
      "Parameters": {
        "QueryString": "CREATE EXTERNAL TABLE IF NOT EXISTS default.stock_summary(`Trade_Date` string,`Ticker` string,`Close` string) ROW FORMAT SERDE   'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe' STORED AS INPUTFORMAT   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat' OUTPUTFORMAT   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat' LOCATION  's3://databucket--9632183891563080/output/' TBLPROPERTIES ('classification'='parquet', 'compressionType'='none', 'typeOfData'='file')",
        "WorkGroup": "primary",
        "ResultConfiguration": {
          "OutputLocation": "s3://databucket--9632183891563080/results/"
        }
      },
      "ResultPath": "$.athenaTable",
      "Next": "Send message with Amazon SNS"
    },
    "Send message with Amazon SNS": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-west-2:078899837862:LabStack-2ff18e01-e448-468f-bff5-9d74a2cc4543-emwMCmDXhZbmHREBbpp2wR-0-TaskCompleteSNS-mnJ0QnCBuQZV",
        "Message": {
          "Input": "The Task is complete!"
        }
      },
      "End": true
    }
  }
}
```

