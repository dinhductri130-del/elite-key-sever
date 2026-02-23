from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta
import json, os, random, string

app = Flask(__name__)
CORS(app)

KEY_FILE = "keys.json"
ADMIN_PASSWORD = "123456"   # 🔥 Đổi mật khẩu admin ở đây

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
    password = data.get("password")

    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"})

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

# 🔥 ADMIN WEB
@app.route("/admin")
def admin_page():
    return render_template_string("""
    <h2>ELITE ADMIN PANEL</h2>
    <input id="password" placeholder="Admin Password"><br><br>
    <input id="custom" placeholder="Custom Key (optional)"><br><br>
    <input id="days" type="number" placeholder="Days"><br><br>
    <button onclick="createKey()">Create Key</button>
    <pre id="result"></pre>

<script>
function createKey(){
    fetch("/create", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            custom: document.getElementById("custom").value,
            days: document.getElementById("days").value,
            password: document.getElementById("password").value
        })
    })
    .then(res=>res.json())
    .then(data=>{
        document.getElementById("result").innerText = JSON.stringify(data,null,2);
    });
}
</script>
    """)

if __name__ == "__main__":
    app.run()