from fastapi import FastAPI, Request, Response, HTTPException, Cookie
from hashlib import sha512
from fastapi.responses import HTMLResponse
from datetime import date
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.access_tokens = []
templates = Jinja2Templates(directory="templates")


@app.get("/hello", response_class=HTMLResponse)
def index_static(request: Request):
    today = date.today()
    today_good_form = today.strftime("%Y-%m-%d")
    return templates.TemplateResponse("today.html", {
        "request": request, "today": today_good_form})


@app.post("/login_session")
def login(user: str, password: str, response: Response):
    if user == '4dm1n' and password == 'NotSoSecurePa$$':

        session_token = sha512(f'{user}{password}12312'.encode()).hexdigest()
        app.access_tokens.append(session_token)
        response.set_cookie(key="session_token",
                            value=session_token)
        return session_token
    else:
        raise HTTPException(status_code=401)


@app.post("/login_token")
def create_cookie(*, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.access_tokens:
        raise HTTPException(status_code=401)
    else:
        return {'token': session_token}
