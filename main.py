import os
import json
import requests
from flask import Flask, request, redirect

app = Flask(__name__)

@app.route("/")
def test():
    return "<p>TESTING SERVER IS RUNNING</p>"

@app.route("/privacy_policy")
def privacy_policy():
    try:
        with open("privacy_policy.html", "rb") as file:
            privacy_policy_html = file.read()
        return privacy_policy_html
    except FileNotFoundError:
        return "<p>Privacy policy not found.</p>", 404

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        try:
            print(json.dumps(request.get_json(), indent=4))
        except Exception as e:
            print(f"Error parsing JSON: {e}")
        return "<p>This is POST Request, Hello Webhook!</p>"

    if request.method == "GET":
        hub_mode = request.args.get("hub.mode")
        hub_challenge = request.args.get("hub.challenge")
        hub_verify_token = request.args.get("hub.verify_token")
        if hub_challenge:
            return hub_challenge
        return "<p>This is GET Request, Hello Webhook!</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
