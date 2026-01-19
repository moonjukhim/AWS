1. Initialize sample Hello Worll app

```bash
sam init

cd sam-app
```

2. Build app

```bash
sam build
# check .aws-sam hidden directory
```

3. Deploy app to the AWS Cloud

```bash
sam deploy --guided
```


4. Run app

```bash
# check Outputs information
# Key               HelloWorldApi
# Description       API Gateway ...
# Value             https://..... <----
```

copy URL to new browser tab

5. Delete app

```bash
sam delete
```


