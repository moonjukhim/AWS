
```text
[Feature Store / 데이터]
        ↓
[Processing Step]
(전처리 & 데이터 분할)
        ↓
[Training Step]
(모델 학습)
        ↓
[Evaluation Step]
(성능 평가)
        ↓
[Model Registration]
(Model Registry에 등록)
        ↓
[Lineage / Artifact 추적]
```

---

### 대안

##### 대안 1 : Python + Git + CI/CD

```text
repo/
 ├─ data_processing.py
 ├─ train.py
 ├─ evaluate.py
 ├─ deploy.py
 └─ .github/workflows/ml.yml
```

```text
Git Push
  ↓
GitHub Actions
  ↓
SageMaker Training / Endpoint API 호출
  ↓
CloudWatch / S3 / Git 기록
```

##### 대안 2 : SageMaker “최소 API만 사용"

##### 대안 3 : MLflow + SageMaker

```text
MLflow UI (통합)
 ├─ Experiment
 ├─ Run
 ├─ Metrics
 ├─ Model Registry
```

##### 대안 4 : Airflow / Prefect / Dagster

```text
[Airflow UI]
  ├─ preprocess
  ├─ train
  ├─ evaluate
  └─ deploy
```