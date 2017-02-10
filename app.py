import os

from flask import Flask, jsonify
import boto3

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
app.config['AWS_SNS_TOPIC'] = os.environ.get('AWS_SNS_TOPIC')
app.config['AWS_SNS_REGION'] = os.environ.get('AWS_SNS_REGION')

sns = boto3.resource(
    'sns',
    aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key = app.config['AWS_SECRET_ACCESS_KEY'],
    region_name = app.config['AWS_SNS_REGION'],
)
topic = sns.Topic(app.config['AWS_SNS_TOPIC'])

@app.route('/')
def index():
    response = topic.publish(
        Message = 'Ding Dong',
    )
    return jsonify(response), {'Access-Control-Allow-Origin': '*'}

if __name__ == '__main__':
    app.run(host='0.0.0.0')
