import os
import json
import requests
from flask import Flask, request, redirect

app = Flask(__name__)

with open('../cwdchat_config.json', 'r') as file:
        config = json.load(file)

app_id = config["app_id"]
app_secret = config["app_secret"]
redirect_uri = "https://ig-bot-junf.onrender.com/your_insta_token"


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
    
@app.route("/login")
def login():
    url = "https://www.instagram.com/oauth/authorize?"
    url = url + f"client_id={int(app_id)}"
    url = url + "&" + f"redirect_uri={redirect_uri}"
    url = url + "&" + f"response_type=code"
    url = url + "&" + f"scope={('instagram_business_basic,instagram_business_content_publish,instagram_business_manage_messages,instagram_business_manage_comments').replace(',','%2C')}"
    return redirect(url)

@app.route("/your_insta_token")
def your_insta_token():
    authorization_code = request.args.get("code") + "#_"
    
    url = f"https://api.instagram.com/oauth/access_token"
    payload = {
        "client_id": int(app_id),
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": authorization_code
        
    }
    response = requests.post(url, data=payload)
    data = response.json()
    # print(json.dumps(data, indent=4))
    user_access_token = data["access_token"]
    return f"Your user token is: {user_access_token[0:5]}..."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
