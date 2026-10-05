# This script does some basic data processing such as string indexing, one hot encoding, vector assembly, and an 80-20 split to produce training and validation datasets.

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import csv
import os
import shutil
import sys
import time

import pyspark
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    OneHotEncoder,
    StringIndexer,
    VectorAssembler,
    VectorIndexer,
)
from pyspark.sql.functions import *
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
)

import pandas as pd

def csv_line(data):
    r = ",".join(str(d) for d in data[1])
    return str(data[0]) + "," + r


def main():
    parser = argparse.ArgumentParser(description="app inputs and outputs")
    parser.add_argument("--s3_input_bucket", type=str, help="s3 input bucket")
    parser.add_argument("--s3_input_key_prefix", type=str, help="s3 input key prefix")
    parser.add_argument("--s3_output_bucket", type=str, help="s3 output bucket")
    parser.add_argument("--s3_output_key_prefix", type=str, help="s3 output key prefix")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("PySparkApp").getOrCreate()

    spark.sparkContext._jsc.hadoopConfiguration().set(
        "mapred.output.committer.class", "org.apache.hadoop.mapred.FileOutputCommitter"
    )

    # Defining the schema corresponding to the input data.
    schema = StructType(
        [
            StructField("age", IntegerType(), True),
            StructField("workclass", StringType(), True),
            StructField("fnlwgt", IntegerType(), True),
            StructField("education", StringType(), True),
            StructField("education_num", IntegerType(), True),
            StructField("marital_status", StringType(), True),
            StructField("occupation", StringType(), True),
            StructField("relationship", StringType(), True),
            StructField("race", StringType(), True),
            StructField("sex", StringType(), True),
            StructField("capital_gain", IntegerType(), True),
            StructField("capital_loss", IntegerType(), True),
            StructField("hours_per_week", IntegerType(), True),
            StructField("native_country", StringType(), True),
            StructField("income", StringType(), True)
        ]
    )

    # Downloading the data from S3 into a Dataframe
    adult_df = spark.read.csv(("s3://" + os.path.join(args.s3_input_bucket, args.s3_input_key_prefix, "spark_adult_data.csv")), 
                              header=False, 
                              schema=schema)

    # StringIndexer on the columns which has categorical value
    categorical_variables = ['workclass', 'education', 'marital_status', 'occupation', 'relationship', 'race', 'sex', 'native_country']

    indexers = [StringIndexer(inputCol=column, outputCol=column+"-index") for column in categorical_variables]

    # one-hot-encoding is being performed on the string-indexed columns
    encoder = OneHotEncoder(
        inputCols=[indexer.getOutputCol() for indexer in indexers],
        outputCols=["{0}-encoded".format(indexer.getOutputCol()) for indexer in indexers]
    )

    # vector-assembler will bring all the features to a 1D vector for us to save easily into CSV format
    assembler = VectorAssembler(inputCols=encoder.getOutputCols(),outputCol="cat_features")
    
    # The pipeline is comprised of the steps added above
    pipeline = Pipeline(stages=indexers + [encoder, assembler])

    adult_df = pipeline.fit(adult_df).transform(adult_df)
    
    adult_df.select('cat_features')
    
    # Combine continuous variables with the categorical variables into a single column.
    num_cols = ['age', 'fnlwgt', 'education_num', 'capital_gain', 'capital_loss', 'hours_per_week']

    assembler = VectorAssembler(inputCols=['cat_features', *num_cols],outputCol='features')

    transformed_adult_df = assembler.transform(adult_df)

    # Split the overall dataset into 80-20 training and validation
    (train_df, validation_df) = transformed_adult_df.randomSplit([0.8, 0.2])
    
    train_df_pd = train_df.toPandas()['features']
    
    validation_df_pd = validation_df.toPandas()['features']
    
    train_features_output_path = os.path.join("/opt/ml/processing/train", "train_features.csv")
    validation_features_output_path = os.path.join("/opt/ml/processing/validation", "validation_features.csv")
    
    train_df_pd.to_csv(train_features_output_path, header=False, index=False)

    validation_df_pd.to_csv(validation_features_output_path, header=False, index=False)
    
    
if __name__ == "__main__":
    main()
