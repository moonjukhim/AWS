### 태스크 4: SageMaker Studio로 자체 컨테이너 사용

##### 태스크 4.2: 처리 컨테이너 만들기

```bash
%mkdir docker

%%writefile docker/Dockerfile
FROM public.ecr.aws/docker/library/python:3.10-slim-bullseye

RUN pip3 install pandas scikit-learn
ENV PYTHONUNBUFFERED=TRUE

ENTRYPOINT ["python3"]
```

##### 태스크 4.2.2: 컨테이너 이미지 빌드

```bash
%%sh

rm /usr/lib/x86_64-linux-gnu/libstdc++.so.6

cp /opt/conda/lib/libstdc++.so.6 /usr/lib/x86_64-linux-gnu/libstdc++.so.6

cd docker

sm-docker build .
```

