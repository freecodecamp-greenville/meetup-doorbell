import os

from flask import Flask, jsonify, request
import boto3

from utils import get_datetime, doorbell_is_active

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
app.config["AWS_SNS_TOPIC"] = os.environ.get("AWS_SNS_TOPIC")
app.config["AWS_SNS_REGION"] = os.environ.get("AWS_SNS_REGION")
app.config["APP_TZ"] = os.environ.get("APP_TZ")

sns = boto3.resource("sns", region_name=app.config["AWS_SNS_REGION"])
topic = sns.Topic(app.config["AWS_SNS_TOPIC"])


@app.after_request
def set_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "content-type"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and request.is_json:
        now = get_datetime(app.config["APP_TZ"])
        active = doorbell_is_active(
            now,
            suppress_dates=os.environ.get("SUPPRESS_DATES"),
            force_active=os.environ.get("FORCE_ACTIVE", "false").lower() == "true",
        )
        if request.get_json().get("action") == "status":
            status = "active" if active else "inactive"
            return jsonify({"status": status})
        elif active and request.get_json().get("action") == "ring":
            message = f"{now.strftime('%H:%M:%S')} Ding Dong"
            response = topic.publish(Message=message)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return jsonify({"message": "Someone will open the door shortly."})
            else:
                return jsonify({"message": "Something went wrong. Please try again."})
        else:
            return jsonify({"message": "Doorbell is inactive at this time."})
    else:
        return jsonify({"message": "Incorrect request type."})


if __name__ == "__main__":
    app.run(host="0.0.0.0")

