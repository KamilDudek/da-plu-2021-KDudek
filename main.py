from fastapi import FastAPI, Request, Response, HTTPException, Cookie, \
    Depends, status
import base64
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, PlainTextResponse
from datetime import date
from fastapi.templating import Jinja2Templates
import secrets
from datetime import datetime

from starlette.responses import RedirectResponse

app = FastAPI()
security = HTTPBasic()

templates = Jinja2Templates(directory="templates")

app.secret_key = f'Very hard to break and strong key to base64' \
                 f'{datetime.now().time()}'
app.access_session = []
app.access_token = []


@app.get("/hello", response_class=HTMLResponse)
def index_static(request: Request):
    today = date.today()
    today_good_form = today.strftime("%Y-%m-%d")
    return templates.TemplateResponse("today.html", {
        "request": request, "today": today_good_form})


def get_session_token(credentials: HTTPBasicCredentials = Depends(security)):
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
        session_token_decode = f'{credentials.username}' \
                               f'{credentials.password}{app.secret_key}'
        session_token_bytes = session_token_decode.encode('ascii')
        base64_bytes = base64.b64encode(session_token_bytes)
        session_token = base64_bytes.decode('ascii')

        return session_token


@app.post("/login_session", status_code=201)
def login_session(response: Response,
                  session_token: str = Depends(get_session_token)):
    response.set_cookie(key="session_token",
                        value=session_token)
    if len(app.access_session) >= 3:
        app.access_session.pop(0)
    app.access_session.append(session_token)

    return {"token": session_token}


@app.post("/login_token", status_code=201)
def login_token(token: str = Depends(get_session_token)):
    if len(app.access_token) >= 3:
        app.access_token.pop(0)
    app.access_token.append(token)
    return {'token': token}


def check_format(access, access_table, format):
    if access not in access_table or access == '':
        raise HTTPException(status_code=401, detail="Unauthorised")
    else:
        if format == 'json':
            return {"message": 'Welcome!'}
        elif format == 'html':
            return HTMLResponse(content="<h1>Welcome!</h1>", status_code=200)
        else:
            return PlainTextResponse(content="Welcome!", status_code=200)


@app.get("/welcome_session")
def welcome_session(format: str = "", session_token: str = Cookie(None)):
    return check_format(session_token, app.access_session, format)


@app.get("/welcome_token")
def welcome_token(token: str = "", format: str = ""):
    return check_format(token, app.access_token, format)


@app.delete("/logout_session")
def logout_session(format: str = "", session_token: str = Cookie(None)):
    if session_token not in app.access_session or session_token == '':
        raise HTTPException(status_code=401, detail="Unauthorised")
    app.access_session.remove(session_token)
    return RedirectResponse(url=f"/logged_out?format={format}",
                            status_code=status.HTTP_302_FOUND)


@app.delete("/logout_token")
def logout_token(token: str = "", format: str = ""):
    if token not in app.access_token or token == '':
        raise HTTPException(status_code=401, detail="Unauthorised")
    app.access_token.remove(token)
    return RedirectResponse(url=f"/logged_out?format={format}",
                            status_code=status.HTTP_302_FOUND)


@app.get("/logged_out")
def logged_out(format: str = ""):
    if format == 'json':
        return {"message": "Logged out!"}
    elif format == 'html':
        return HTMLResponse(content="<h1>Logged out!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Logged out!", status_code=200)
