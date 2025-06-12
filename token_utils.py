import yaml
import requests
import os
import json

GOOGLE_ADS_YAML_PATH = "google-ads.yaml"
TEMP_TOKEN_PATH = "tmp_refresh_token.json"


def is_token_valid():
    with open(GOOGLE_ADS_YAML_PATH, "r") as f:
        config = yaml.safe_load(f)

    data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "refresh_token": config["refresh_token"],
        "grant_type": "refresh_token"
    }

    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    return response.status_code == 200


def update_refresh_token_from_file():
    if not os.path.exists(TEMP_TOKEN_PATH):
        print("❌ Временный файл токена не найден.")
        return False

    with open(TEMP_TOKEN_PATH, "r") as f:
        data = json.load(f)

    new_token = data.get("refresh_token")
    if not new_token:
        print("❌ Токен не найден в JSON.")
        return False

    with open(GOOGLE_ADS_YAML_PATH, "r") as f:
        config = yaml.safe_load(f)

    config["refresh_token"] = new_token

    with open(GOOGLE_ADS_YAML_PATH, "w") as f:
        yaml.safe_dump(config, f)

    os.remove(TEMP_TOKEN_PATH)
    print("✅ Refresh token обновлён в google-ads.yaml.")
    return True