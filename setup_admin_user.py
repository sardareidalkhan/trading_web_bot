# ✅ setup_admin_user.py

import hashlib
import json
from datetime import datetime

# This must match app/auth.py
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

users = {
    "admin@bot.com": {
        "password": hash_password("admin123$$$=+"),
        "token": None,
        "last_login": datetime.utcnow().isoformat()
    }
}

with open("app/users.json", "w") as f:
    json.dump(users, f, indent=2)

print("✅ admin@bot.com user created successfully.")
