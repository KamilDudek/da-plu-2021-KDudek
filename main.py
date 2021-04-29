from fastapi import FastAPI, Request, Response, HTTPException, Cookie
import base64
from typing import Optional
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
def login(response: Response, user: Optional[str] = None,
          password: Optional[str] = None):
    if user == 'a' and password == 'a':

        session_token_uncode = f'{user}{password}dfsds'
        session_token_bytes = session_token_uncode.encode('ascii')
        base64_bytes = base64.b64encode(session_token_bytes)
        session_token = base64_bytes.decode('ascii')
        app.access_tokens.append(session_token)
        response.set_cookie(key="session_token",
                            value=session_token)
        return {'token': session_token}
    else:
        raise HTTPException(status_code=401)


@app.post("/login_token")
def create_cookie(*, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.access_tokens:
        raise HTTPException(status_code=401)
    else:
        return {'token': session_token}
