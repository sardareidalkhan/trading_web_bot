# FULLY UPDATED main.py with all required admin panel features
from fastapi import FastAPI, Request, Form, Cookie, Response, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import hashlib
import logging
import subprocess
import sys
import uuid
import os
import json
from datetime import datetime, timedelta

from app.auth import (
    authenticate_user,
    get_user_by_token,
    logout_user,
    load_users,
    save_users,
    hash_password
)
from app.ai_engine import generate_crypto_signal
from app.log_utils import log_prediction
from ai_analyzer import get_signal_from_chart

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
selected_timeframe = "1m"

def get_pakistan_time():
    return datetime.utcnow() + timedelta(hours=5)

def get_client_device_id(request: Request):
    ua = request.headers.get("user-agent", "")
    return hashlib.sha256((ua + "fixed-salt").encode()).hexdigest()

async def get_current_user(request: Request, token: str = Cookie(default=None), admin_token: str = Cookie(default=None)):
    cookie_token = admin_token or token
    if not cookie_token:
        return None

    user = get_user_by_token(cookie_token)
    if not user:
        return None

    users = load_users()
    user_data = users.get(user["username"])
    if not user_data or not user_data.get("active", True):
        return None

    now = get_pakistan_time()
    expiry = user_data.get("expires_at")
    if expiry:
        try:
            expiry_dt = datetime.fromisoformat(expiry)
            if now > expiry_dt:
                user_data["active"] = False
                save_users(users)
                return None
        except Exception as e:
            logger.error(f"Invalid expiry format: {expiry}")

    user_data["last_login"] = now.isoformat()
    save_users(users)

    current_id = get_client_device_id(request)
    if user_data.get("device_id") and user_data["device_id"] != current_id:
        return None

    return {"username": user["username"]}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "symbol": "",
        "prediction": None,
        "timeframe": "",
        "expiry": "",
        "platform": "",
        "user": user
    })

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login_submit(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    device_id = get_client_device_id(request)
    result = authenticate_user(username, password, device_id=device_id)

    if result["success"]:
        response = RedirectResponse(url="/", status_code=302)
        cookie_name = "admin_token" if username == "admin@bot.com" else "token"
        response.set_cookie(key=cookie_name, value=result["token"], httponly=True)
        return response

    return templates.TemplateResponse("login.html", {"request": request, "error": result["message"]})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, platform: str = Form(...), symbol: str = Form(...),
                  timeframe: str = Form(...), expiry: str = Form(...),
                  user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    global selected_timeframe
    try:
        selected_timeframe = timeframe.strip()
        session_id = str(uuid.uuid4())
        user_dir = os.path.join("sessions", session_id)
        os.makedirs(user_dir, exist_ok=True)

        if platform.lower() == 'quotex':
            subprocess.run([sys.executable, "chart_capture.py", symbol, timeframe, user_dir])
            result = get_signal_from_chart(timeframe=timeframe, expiry=expiry, image_dir=user_dir)
            direction = result.get("direction", "ERROR")
            confidence = result.get("confidence", 0)
        else:
            result = generate_crypto_signal(symbol, timeframe)
            direction = result["signal"]
            confidence = result["confidence"]

        prediction = {
            'direction': direction,
            'confidence': confidence,
            'expiry_time': expiry,
            'entry_delay_seconds': result.get("entry_delay", 0),
            'error': result.get("error", None),
            'prediction_source': "ML model" if platform.lower() == 'quotex' else "Rule-based"
        }

        log_prediction(
            user_email=user["username"],
            symbol=symbol,
            platform=platform,
            timeframe=timeframe,
            direction=direction,
            confidence=confidence
        )

        return templates.TemplateResponse("index.html", {
            "request": request,
            "symbol": symbol,
            "prediction": prediction,
            "timeframe": timeframe,
            "expiry": expiry,
            "platform": platform,
            "user": user
        })

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        prediction = {
            'direction': 'ERROR',
            'confidence': 0,
            'expiry_time': expiry,
            'entry_delay_seconds': 0,
            'error': f'Error: {str(e)}',
            'prediction_source': "Unknown"
        }
        return templates.TemplateResponse("index.html", {
            "request": request,
            "symbol": symbol,
            "prediction": prediction,
            "timeframe": timeframe,
            "expiry": expiry,
            "platform": platform,
            "user": user
        })

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user: dict = Depends(get_current_user)):
    if not user or user["username"] != "admin@bot.com":
        return RedirectResponse(url="/login")

    users = load_users()
    now = get_pakistan_time()
    current_date = now.strftime("%Y-%m-%d")

    for u in users.values():
        if u.get("expires_at"):
            try:
                expiry = datetime.fromisoformat(u["expires_at"])
                delta = expiry - now
                if delta.total_seconds() <= 0:
                    u["active"] = False
                    u["countdown"] = "Expired"
                else:
                    u["countdown"] = str(delta).split('.')[0]
            except:
                u["countdown"] = "Invalid"

    save_users(users)

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user": user,
        "users": users,
        "user_count": len(users),
        "current_date": current_date
    })

@app.get("/admin/user-table", response_class=HTMLResponse)
async def refresh_user_table(request: Request, user: dict = Depends(get_current_user)):
    if not user or user["username"] != "admin@bot.com":
        return HTMLResponse("Unauthorized", status_code=403)

    users = load_users()
    now = get_pakistan_time()

    for u in users.values():
        if u.get("expires_at"):
            try:
                expiry = datetime.fromisoformat(u["expires_at"])
                if now > expiry:
                    u["active"] = False
                    u["countdown"] = "Expired"
                else:
                    u["countdown"] = str(expiry - now).split('.')[0]
            except:
                u["countdown"] = "Invalid"

    save_users(users)

    return templates.TemplateResponse("partials/user_table.html", {
        "request": request,
        "users": users
    })

# ✅ UPDATED toggle-user logic with expiry prompt
@app.post("/admin/toggle-user")
async def toggle_user(
    email: str = Form(...),
    days: int = Form(0),
    hours: int = Form(0),
    minutes: int = Form(0)
):
    users = load_users()
    if email in users and email != "admin@bot.com":
        user = users[email]
        if not user.get("active", True):  # Enabling a disabled user
            now = get_pakistan_time()
            expiry = now + timedelta(days=days, hours=hours, minutes=minutes)
            user["expires_at"] = expiry.isoformat()
            user["active"] = True
        else:
            user["active"] = False
        save_users(users)
    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/create-user")
async def create_user_admin(
    username: str = Form(...),
    password: str = Form(...),
    days: int = Form(0),
    hours: int = Form(0),
    minutes: int = Form(0)
):
    now = get_pakistan_time()
    expiry_dt = now + timedelta(days=days, hours=hours, minutes=minutes)
    expiry_str = expiry_dt.isoformat()

    users = load_users()
    users[username] = {
        "password": hash_password(password),
        "token": "",
        "device_id": None,
        "active": True,
        "expires_at": expiry_str,
        "last_login": ""
    }
    save_users(users)
    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/delete-user")
async def delete_user(email: str = Form(...)):
    if email != "admin@bot.com":
        users = load_users()
        if email in users:
            del users[email]
            save_users(users)
    return RedirectResponse("/admin", status_code=302)

@app.get("/selected-timeframe")
async def get_selected_timeframe():
    return JSONResponse(content={"timeframe": selected_timeframe})

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Trading Bot API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Trading Bot API shutting down")
