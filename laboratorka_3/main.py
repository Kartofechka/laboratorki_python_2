import uuid
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import hashlib
from enum import Enum
from dataclasses import dataclass


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
USERS = "users.csv"
SESSION_TTL = timedelta(1)
sessions = {}
white_urls = ["/", "/login", "/logout"]


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="logs.log",
    filemode="a", encoding="utf-8"
)
logger = logging.getLogger(__name__)

# Контроь авторизации и сессии
@app.middleware("http")
async def check_session(request: Request, call_next):
    path = request.url.path
    if path.startswith("/static") or path.startswith("/assets") or path in white_urls:
        return await call_next(request)

    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login")

    last_active = sessions[session_id]
    if datetime.now() - last_active > SESSION_TTL:
        del sessions[session_id]
        return RedirectResponse(url="/login")
    
    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



class UserRole(Enum):
    USER = "hamster"
    ADMIN = "admin"

@dataclass
class User:
    username: str
    password: str
    role: UserRole


    def from_row(row):
        return User(
            username=row["user"],
            password=row["pass"],
            role=UserRole(row["role"])
        )

    def load_users(file):
        df = pd.read_csv(file)
        users = []
        for i in range(len(df)):
            row = df.iloc[i]
            username = row["user"]
            password = row["pass"]
            role = UserRole(row["role"])
            user = User(username, password, role)
            users.append(user)
        return users


    def find(username, users):
        for user in users:
            if user.username == username:
                return user
        return None


    def save_user(file, new_user):
        df = pd.read_csv(file)
        new_row = {
            "user": new_user.username,
            "pass": new_user.password,
            "role": new_user.role.value
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(file, index=False)




@app.post("/login")
def login(request: Request,
          username: str = Form(...),
          password: str = Form(...)):
    users = User.load_users(USERS)
    user_agent = request.headers.get("user-agent", "неизвестно")
    client_host = request.client.host if request.client else "неизвестно"
    user = User.find(username, users)
    if user:
        logger.info(f"[ПОПЫТКА ВХОДА] пользователь: {username} ip: {client_host} параметры системы: {user_agent}")
        session_id = request.cookies.get("session_id")
        if session_id in sessions:
            del sessions[session_id]
            return templates.TemplateResponse("login.html", {
                "request": request,
                "message": "Глупец, ты уже был авторизован"
            })
        if user.password == hashlib.sha256(password.encode()).hexdigest():
            session_id = str(uuid.uuid4())
            sessions[session_id] = datetime.now()
            response = RedirectResponse(url=f"/home/{username}", status_code=302)
            response.set_cookie(key="session_id", value=session_id)
            response.set_cookie(key="user_name", value=username)
            response.set_cookie(key="role", value=user.role)
            logger.info(f"[УСПЕШНЫЙ ВХОД] пользователь: {username} session_id: {session_id}")
            return response
        logger.warning(f"[ОШИБКА АВТОРИЗАЦИИ] неверный пароль, пользователь: {username} ")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Глупец, введи правильный пароль"
        })
    logger.warning(f"[ОШИБКА АВТОРИЗАЦИИ] логин не найден, пользователь: {username}")
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Глупец, введи правильный логин"
    })


@app.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    user_name = request.cookies.get("user_name")
    session_id = request.cookies.get("session_id")
    logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
    logger.info(f"[ЗАВЕРШЕНИЕ СЕССИИ] пользователь: {user_name} session_id: {session_id}")
    if session_id in sessions:
        del sessions[session_id]
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": "Вы вышли из системы"
    })


@app.get("/home/admin", response_class=HTMLResponse)
def login_page(request: Request):
    user_name = request.cookies.get("user_name")
    logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
    logger.info(f"Админ {user_name} перешел в main")
    return templates.TemplateResponse("main.html", {"request": request})



@app.get("/to_login", response_class=HTMLResponse)
def to_login(request: Request):
    user_name = request.cookies.get("user_name")
    session_id = request.cookies.get("session_id")
    logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
    logger.info(f"Переход на страницу авторизации: {user_name} | {session_id}")
    return RedirectResponse(url="/login", status_code=302)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        user_name = request.cookies.get("user_name")
        logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
        logger.warning(f"[404] пользователь: {user_name} адреса: {request.url.path}")
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
    return await http_exception_handler(request, exc)


@app.get("/register", response_class=HTMLResponse)
def get_register_page(request: Request):
    user_name = request.cookies.get("user_name")
    session_id = request.cookies.get("session_id")
    if user_name == "admin":
        logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
        logger.info(f"Переход на страницу регистрации: {user_name} | {session_id}")
        return templates.TemplateResponse("registration.html", {"request": request})
    logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
    logger.warning(f"[ДОСТУП ЗАКРЫТ] пользователь {user_name} пытался перейти на /register")
    return templates.TemplateResponse("403.html", {"request": request})


@app.post("/register")
def register(request: Request,
            reg_name: str = Form(...),
            reg_password: str = Form(...)):
    users = User.load_users(USERS)
    if User.find(reg_name, users):
        return templates.TemplateResponse("registration.html", {
                "request": request,
                "message": "Имя уже занято"
            })
    new_user = User(reg_name, hashlib.sha256(reg_password.encode()).hexdigest(), UserRole.USER)
    User.save_user(USERS, new_user)
    logger.info(f"[РЕГИСТРАЦИЯ НОВОГО ХОМЯЧКА] новый пользователь: {reg_name}")
    return templates.TemplateResponse("main.html", {
        "request": request,
        "message": "Регистрация нового пользователя успешна."
    })


@app.get("/home/{username}", response_class=HTMLResponse)
def login_page(request: Request):
    user_name = request.cookies.get("user_name")
    session_id = request.cookies.get("session_id")
    logger.info(f"[ПЕРЕХОД] пользователь: {user_name} адрес: {request.url.path}")
    logger.info(f"Хомячок: {user_name} | {session_id}")
    return templates.TemplateResponse("hamster.html", {"request": request})

