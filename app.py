import os
from datetime import datetime

from flask import Flask, jsonify, request
import boto3
import pytz

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('APP_AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('APP_AWS_SECRET_ACCESS_KEY')
app.config['AWS_SNS_TOPIC'] = os.environ.get('AWS_SNS_TOPIC')
app.config['AWS_SNS_REGION'] = os.environ.get('AWS_SNS_REGION')
app.config['APP_TZ'] = os.environ.get('APP_TZ')
app.config['SUPPRESS_DATES'] = os.environ.get('SUPPRESS_DATES')

sns = boto3.resource(
    'sns',
    aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key = app.config['AWS_SECRET_ACCESS_KEY'],
    region_name = app.config['AWS_SNS_REGION'],
)
topic = sns.Topic(app.config['AWS_SNS_TOPIC'])

def get_datetime(timezone):
    """Returns datetime object as given timezone."""
    tz = pytz.timezone(timezone)
    return pytz.utc.localize(datetime.utcnow()).astimezone(tz)

def doorbell_is_active():
    now = get_datetime(app.config['APP_TZ'])
    if app.config['SUPPRESS_DATES']:
        suppress_dates = [
            datetime.strptime(date, '%Y-%m-%d').date()
            for date in app.config['SUPPRESS_DATES'].split(',')
        ]
        if now.date() in suppress_dates:
            return False
    return now.weekday() == 3 and now.hour >= 18 and now.hour < 21

@app.after_request
def set_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and request.is_json:
        if request.get_json().get('action') == 'status':
            status = 'active' if doorbell_is_active() else 'inactive'
            return jsonify({
                'status': status
            })
        elif doorbell_is_active() and request.get_json().get('action') == 'ring':
            now = get_datetime(app.config['APP_TZ'])
            message = '{hour:02d}:{minute:02d} Ding Dong'.format(
                hour = now.hour,
                minute = now.minute,
            )
            response = topic.publish(
                Message = message,
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return jsonify({
                    'message': 'Someone will open the door shortly.'
                })
            else:
                return jsonify({
                    'message': 'Something went wrong. Please try again.'
                })
        else:
            return jsonify({
                'message': 'Doorbell is inactive at this time.'
            })
    else:
        return jsonify({
            'message': 'Incorrect request type.',
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0')
