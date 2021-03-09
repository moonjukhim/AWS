import sys
from random import random
from operator import add

from pyspark.sql.session import SparkSession
from pyspark.sql.functions import unix_timestamp,udf,hour,minute,from_unixtime


if __name__ == "__main__":
    """
        Usage:
    """
    output_file = sys.argv[1]
    spark = SparkSession.builder\
            .getOrCreate()


    for x in range(6,7):
        s3_location = "s3://aws-tc-largeobjects/AWS-200-BIG/v3.1/lab-6-spark/trip?data/yellow_tripdata_2015-" + str(x).zfill(2) +".csv"
        time_format = "yyyy-MM-dd HH-mm-ss"

        # We will use spark Dataframes api to read the New York Taxi dataset into a spark Dataframe
        # The dataframe is automatically read the schema using option("inferSchema","true")
        # For printing the schema of a dataframe use df.printSchema()
        df = spark.read.option("header","true")\
             .option("inferSchema","true")\
             .csv(s3_location)

        # Using a bounded box for New York city using pickup latitude and longitude
        df1 = df[(df['pickup_latitude'] < 40.917577)\
                 & (df['pickup_latitude'] > 40.477399)\
                 & (df['pickup_longitude'] > -74.259090)\
                 & (df['pickup_longitude'] < -73.700272)]

        # Some data points have not registered with correct dropoff latitude and longtitude
        # and show up as zero
        df2 = df1[(df1['dropoff_longitude'] < 0)\
              & (df1['dropoff_latitude'] > 0)\
              &(df1['pickup_longitude'] != df1['dropoff_longitude'])\
              & (df1['pickup_latitude'] != df1['dropoff_latitude'])]

        # Adding a time duration for each taxi ride.
        #For machine learning, the hour of the day integer as well as day of the
        #week integer will be important for the algorithm to learn from one
        #month worth of datapoints.
        time_duration = unix_timestamp("tpep_dropoff_datetime",format = time_format)\
                      - unix_timestamp("tpep_pickup_datetime", format = time_format)
        df3 = df2.withColumn("time_duration",time_duration)\
                 .withColumn("hour",hour(df2.tpep_pickup_datetime))\
                 .withColumn("dayOfWeek",from_unixtime(unix_timestamp\
                            (df1.tpep_pickup_datetime,time_format),"uuuuu").cast("Integer"))

        # A Taxi will not drive more than 500 miles for a single ride.
        # A taxi ride will be more than 10 seconds even if you go just 10 metres
        df4 = df3[(df3['trip_distance'] < 500)\
                  & (df3['time_duration'] > 10)]

        # Remove negative cost fields
        df5 = df4[(df4['fare_amount'] > 0)\
                  & (df4['extra'] >= 0)\
                  & (df4['mta_tax'] >= 0)\
                  & (df4['tip_amount'] >= 0)\
                  & (df4['tolls_amount'] >= 0)\
                  & (df4['improvement_surcharge'] >= 0)\
                  & (df4['total_amount'] > 0)]

        #df5.coalesce(1).write.option("header","true").csv(output_file + "/2015/" + str(x).zfill(2) + ".csv")
        df5.write.csv(output_file + "/2015/" + str(x).zfill(2) + ".csv")
