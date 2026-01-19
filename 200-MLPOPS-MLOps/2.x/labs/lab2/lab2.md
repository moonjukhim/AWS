### StepFunctionsPipeline

    - Source
        - buildspec.yaml
        - requirements.txt
        - state_machine_manager.py
    - Build

    ```yaml
    # buildspec.yaml
    phases:
        install:
            commands:
            - python --version
            - pip install --upgrade pip
            - pip install --upgrade stepfunctions
        pre_build:
            commands:
            - cd $CODEBUILD_SRC_DIR
        build:
            commands:
            - cd $CODEBUILD_SRC_DIR
            - python state_machine_manager.py
        post_build:
            commands:
            - echo Build completed on `date`
    ```

---

### TrainDeployModelPipeline

    - source
        - ml_service
            - app.py
            - nginx.conf
            - server.py
            - wsgi.py
        - model
            - model_random.py
            - model.py
        - output
            - decision-tree-model.pkl
        - buildspec.yml
        - Dockerfile
        - requirements.txt
        - start_local_serve.sh
        - test_local_serve.sh
    - build
    - train

```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 064091573531.dkr.ecr.us-west-2.amazonaws.com
  build:
    commands:
      - chmod -R 775 ml_service
      - echo Decision Tree Permissions `cd ml_service && ls -la`
      - docker build -t $IMAGE_NAME:$RunId .
      - docker tag $IMAGE_NAME:$RunId $ECR_URI:$RunId
  post_build:
    commands:
      - docker push $ECR_URI:$RunId
```
