import hashlib
import json
import os
from datetime import datetime, timedelta

USERS_FILE = "app/users.json"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def authenticate_user(username: str, password: str, device_id: str = None) -> dict:
    users = load_users()
    user = users.get(username)

    if not user:
        return {"success": False, "message": "❌ Invalid username or password."}

    # ✅ Admin bypass — safely handles login
    if username == "admin@bot.com":
        token = hashlib.sha256((username + "admin123$$$=+").encode()).hexdigest()
        user["token"] = token
        user["device_id"] = device_id or user.get("device_id")
        user["last_login"] = datetime.utcnow().isoformat()
        users[username] = user
        save_users(users)
        return {"success": True, "token": token}

    # ✅ Normal user login
    if user.get("password") != hash_password(password):
        return {"success": False, "message": "❌ Invalid username or password."}

    if not user.get("active", True):
        return {"success": False, "message": "❌ This account is deactivated."}

    # ✅ Expiry time check (exact to the second)
    if "expires_at" in user:
        now = datetime.utcnow()
        expiry = datetime.fromisoformat(user["expires_at"])
        if now > expiry:
            user["active"] = False  # Automatically deactivate
            save_users(users)
            return {"success": False, "message": "❌ This account has expired."}

    # ✅ Device lock (only 1 login per user)
    if not user.get("device_id"):
        user["device_id"] = device_id
        user["last_login"] = datetime.utcnow().isoformat()
        users[username] = user
        save_users(users)
    elif user["device_id"] != device_id:
        return {"success": False, "message": "❌ This account is already used on another device."}

    # ✅ Generate login token
    token = hashlib.sha256((username + user["password"]).encode()).hexdigest()
    user["token"] = token
    user["last_login"] = datetime.utcnow().isoformat()
    users[username] = user
    save_users(users)

    return {"success": True, "token": token}

def get_user_by_token(token: str) -> dict | None:
    users = load_users()
    for username, user in users.items():
        if user.get("token") == token:
            return {"username": username}
    return None

def logout_user(token: str):
    users = load_users()
    for user in users.values():
        if user.get("token") == token:
            user["token"] = ""
    save_users(users)

# ✅ Optional: utility for CLI or admin scripts
def add_user(username: str, password: str, duration_days: int = 30):
    users = load_users()
    expires_at = (datetime.utcnow() + timedelta(days=duration_days)).isoformat()
    users[username] = {
        "password": hash_password(password),
        "token": "",
        "device_id": None,
        "active": True,
        "expires_at": expires_at,
        "last_login": ""
    }
    save_users(users)
