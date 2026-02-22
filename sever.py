from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json, os, random, string

app = Flask(__name__)
KEY_FILE = "keys.json"

def load_keys():
    if not os.path.exists(KEY_FILE):
        return {}
    with open(KEY_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(KEY_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def home():
    return "ELITE KEY SERVER ONLINE"

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    key = data.get("key")
    keys = load_keys()

    if key not in keys:
        return jsonify({"status": "invalid"})

    expire_date = datetime.strptime(keys[key], "%Y-%m-%d")

    if datetime.now() > expire_date:
        return jsonify({"status": "expired"})

    return jsonify({"status": "valid"})

@app.route("/create", methods=["POST"])
def create_key():
    data = request.json
    days = int(data.get("days", 1))
    custom = data.get("custom")

    keys = load_keys()

    if custom:
        key = custom
    else:
        key = "ELITE-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    expire = datetime.now() + timedelta(days=days)
    keys[key] = expire.strftime("%Y-%m-%d")
    save_keys(keys)

    return jsonify({"key": key, "expire": keys[key]})

@app.route("/list")
def list_keys():
    return jsonify(load_keys())

if __name__ == "__main__":
    app.run()