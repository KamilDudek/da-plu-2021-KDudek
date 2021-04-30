from fastapi import FastAPI, Request, Response, HTTPException, Cookie, Depends, \
    status
import base64
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from datetime import date
from typing import Optional
from fastapi.templating import Jinja2Templates
import secrets

app = FastAPI()
security = HTTPBasic()

templates = Jinja2Templates(directory="templates")

app.access_tokens = ''


@app.get("/hello", response_class=HTMLResponse)
def index_static(request: Request):
    today = date.today()
    today_good_form = today.strftime("%Y-%m-%d")
    return templates.TemplateResponse("today.html", {
        "request": request, "today": today_good_form})


def get_current_username(response: Response,
                         credentials: HTTPBasicCredentials = Depends(
                             security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password,
                                              "NotSoSecurePa$$")

    if not (correct_username or correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        session_token_decode = f'{credentials.username}{credentials.password}dfsds'
        session_token_bytes = session_token_decode.encode('ascii')
        base64_bytes = base64.b64encode(session_token_bytes)
        session_token = base64_bytes.decode('ascii')
        app.access_tokens = session_token
        response.set_cookie(key="session_token",
                            value=session_token)
    return credentials.username


@app.post("/login_session", status_code=201)
def login_session(username: str = Depends(get_current_username)):
    return {"token": app.access_tokens}


@app.post("/login_token", status_code=201)
def login_token(username: str = Depends(get_current_username)):
    return {'token': app.access_tokens}


@app.get("/welcome_session")
def login(*, response: Response, session_token: str = Cookie(None)):
    if session_token != app.access_tokens:
        raise HTTPException(status_code=401, detail="Unauthorised")
    else:
        return {"message": "Secure Content"}


@app.get("/welcome_token")
def login(*, response: Response, session_token: str,
          format: Optional[str] = None):
    if session_token != app.access_tokens:
        raise HTTPException(status_code=401, detail="Unauthorised")
    else:
        if format == 'json':
            return {"message": "Welcome!"}
        elif format == 'html':
            return HTMLResponse(content="<h1>Welcome!</h1>", status_code=200)
        else:
            return f'Welcome!'
