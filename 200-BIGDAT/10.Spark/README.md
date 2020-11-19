# 모듈10: Amazon EMR의 Apache Spark

--- 

# Demo

```python
spark = SparkSession.builder.appName('Amazon reviews word count').getOrCreate()
df.selectExpr("explode(split(lower(review_body), ' ')) as words").groupBy("words").count().explain()
 
quit()
```
