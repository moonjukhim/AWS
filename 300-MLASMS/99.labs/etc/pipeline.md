```python
pipeline = Pipeline(
    name = pipeline_name,
    parameters = [ ],
    steps = [step_process, step_tuning, step_eval, step_cond],
    sagemaker_session = sagemaker_session
)


sklearn_processor = SKLearnProcessor()
# ChurnModelProcess [*step_process, step_tuning, step_eval, step_cond]
step_process = ProcessingStep(
        name = "ChurnModelProcess",
        processor = sklearn_processor,
        outputs = [],
        job_arguments = ["--featuregroupname",feature_group_name,"--default-bucket",default_bucket,"--region",region],
        code = f"s3://{default_bucket}/input/code/processfeaturestore.py",
    )

# ChurnHyperParameterTuning [step_process, *step_tuning, step_eval, step_cond]
step_tuning = TuningStep(
    name = "ChurnHyperParameterTuning",
    tuner = HyperparameterTuner(),
    inputs = {},
    )

# ChurnEvalBestModel [step_process, step_tuning, *step_eval, step_cond]
step_eval = ProcessingStep(
    name = "ChurnEvalBestModel",
    processor = script_eval,
    inputs = [],       outputs = [],
    code = f"s3://{default_bucket}/input/code/evaluate.py",
    property_files = [evaluation_report],
)


# ChurnCreateModel
step_create_model = CreateModelStep(
    name = "ChurnCreateModel",
    model = model,
    inputs = inputs,
)


# RegisterChurnModel
step_register = RegisterModel(
    name = "RegisterChurnModel",
    estimator = xgb_train,
    model_data = step_tuning.get_top_model_s3_uri(top_k = 0, s3_bucket = default_bucket, prefix = "output"),
    content_types = ["text/csv"],                               response_types = ["text/csv"],
    inference_instances = ["ml.t2.medium", "ml.m5.large"],      transform_instances = ["ml.m5.large"],
    model_package_group_name = model_package_group_name,
    model_metrics = model_metrics,
)

# ChurnModelConfigFile
step_config_file = ProcessingStep(
    name = "ChurnModelConfigFile",
    processor = script_processor,
    code = f"s3://{default_bucket}/input/code/generate_config.py",
    job_arguments = [],
    depends_on = [step_create_model.name]
)

# ChurnTransform
step_transform = TransformStep(
    name = "ChurnTransform",
    transformer = transformer,
    inputs = TransformInput(data = batch_data, content_type = "text/csv", join_source = "Input", split_type = "Line")
    )

# ClarifyProcessingStep
step_clarify = ProcessingStep(
    name = "ClarifyProcessingStep",
    processor = clarify_processor,
    inputs = [data_input, config_input],
    outputs = [result_output],
    depends_on = [step_config_file.name]
)

# CheckAUCScoreChurnEvaluation [step_process, step_tuning, step_eval, *step_cond]
step_cond = ConditionStep(
    name = "CheckAUCScoreChurnEvaluation",
    conditions = [cond_lte], # 0.75보다 큰 경우
    if_steps = [step_create_model, step_config_file, step_transform, step_clarify, step_register],
    else_steps = [],
)
```
