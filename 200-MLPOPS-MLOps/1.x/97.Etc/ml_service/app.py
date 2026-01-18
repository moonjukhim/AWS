import sys
import os
import io
import json
import traceback
import multiprocessing
import subprocess
import flask
import pandas as pd

# This directory is the communication channel between Sagemaker and your container
prefix = '/opt/ml'

# Here, Sagemaker will store the dataset copyied from S3
input_path = os.path.join(prefix, 'input/data')
channel_name = 'training'
training_path = os.path.join(input_path, channel_name)
# If something bad happens, write a failure file with the error messages and store here
output_path = os.path.join(prefix, 'output')
# Everything you store here will be packed into a .tar.gz by Sagemaker and store into S3
model_path = os.path.join(prefix, 'model')
# These are the hyperparameters you will send to your algorithms through the Estimator
param_path = os.path.join(prefix, 'input/config/hyperparameters.json')

sys.path.insert(0, '/opt/model_code')
import model
import server


class Predictor(object):
    model = None

    @classmethod
    def get_model(cls):
        if cls.model is None:            
            cls.model = model.load_model(model_path)
        return cls.model

    @classmethod
    def predict(cls, data):
        _model = cls.get_model()
        return model.predict(data, _model)


def start_train_job():
    try:
        with open(param_path, 'r') as hp:
            hyperparameters = json.loads(hp.read())
        _model = model.train_model(training_path, hyperparameters)
        model.save_model(model_path, _model)
    except Exception as ex:
        # Write out an error file. This will be returned as the failureReason in the
        # DescribeTrainingJob result.
        trc = traceback.format_exc()
        with open(os.path.join(output_path, 'failure'), 'w') as s:
            s.write('Exception during training: ' + str(ex) + '\n' + trc)
        # Printing this causes the exception to be in the training job logs, as well.
        print('Exception during training: ' + str(ex) + '\n' + trc, file=sys.stderr)
        # A non-zero exit code causes the training job to be marked as Failed.
        sys.exit(255)


# The flask app for serving predictions
app = flask.Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    health = Predictor.get_model() is not None
    status = 200 if health else 404
    return flask.Response(response='\n', status=status, mimetype='application/json')

@app.route('/invocations', methods=['POST'])
def invoke():
    data = None
    if flask.request.content_type == 'text/csv':
        raw_data = flask.request.data.decode('utf-8')
        data = io.StringIO(raw_data)
    else:
        return flask.Response(response='Invalid request data type, only csv is supported.', status=415, mimetype='text/plain')
    
    predictions = Predictor.predict(data)
    print('Invoked with {} records'.format(predictions.shape[0]))
    out = io.StringIO()
    pd.DataFrame({'results': predictions}).to_csv(out, header=False, index=False)
    return flask.Response(response=out.getvalue(), status=200, mimetype='text/csv')

if __name__ == "__main__":
    if len(sys.argv) < 2 or ( not sys.argv[1] in [ "serve", "train", "test"] ):
        raise Exception("Invalid argument: you must specify 'train' for training mode or 'serve' predicting mode") 

    train = sys.argv[1] == "train"
    test = sys.argv[1] == "test"

    if train:
        start_train_job()

    elif test:
        for line in sys.stdin:
            data_in = io.StringIO(line)
            predictions = Predictor.predict(data_in)
            out = io.StringIO()
            pd.DataFrame({'results': predictions}).to_csv(out, header=False, index=False)
            print (out.getvalue().rstrip())
            
    else: # serve
        cpu_count = multiprocessing.cpu_count()
        model_server_timeout = os.environ.get('MODEL_SERVER_TIMEOUT', 60)
        model_server_workers = int(os.environ.get('MODEL_SERVER_WORKERS', cpu_count))
        server.start_server(model_server_timeout, model_server_workers)        
