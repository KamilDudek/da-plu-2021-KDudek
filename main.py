from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import date
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/hello", response_class=HTMLResponse)
def index_static(request: Request):
    today = date.today()
    today_good_form = today.strftime("%Y-%m-%d")
    return templates.TemplateResponse("today.html", {
        "request": request, "today": today_good_form})
