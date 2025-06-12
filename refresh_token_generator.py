from flask import Flask, redirect, request
import requests
import webbrowser
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://ads.factum.work/oauth2callback"
SCOPE = "https://www.googleapis.com/auth/adwords"
TEMP_TOKEN_PATH = "tmp_refresh_token.json"

@app.route("/")
def start():
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPE}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return redirect(auth_url)

@app.route("/oauth2callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Ошибка: нет кода авторизации."

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    if response.ok:
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")

        if refresh_token:
            with open(TEMP_TOKEN_PATH, "w") as f:
                json.dump({"refresh_token": refresh_token}, f)
            return "✅ Refresh token получен и сохранён. Можете закрыть окно."
        else:
            return "⚠️ Refresh token отсутствует в ответе."

    return f"Ошибка: {response.text}"

if __name__ == "__main__":
    webbrowser.open("https://ads.factum.work:5000/")
    app.run(host="0.0.0.0", port=5000)