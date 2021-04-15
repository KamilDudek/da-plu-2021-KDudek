from fastapi import FastAPI, HTTPException, Response
import hashlib

app = FastAPI()


@app.get("/", status_code=200)
def root():
    return {"message": "Hello World"}


@app.get("/method", status_code=200)
def check_method():
    return {"method": "GET"}


@app.get("/auth", response_class=Response, status_code=204)
def auth_method(password: str, password_hash: str):
    m = hashlib.sha512()
    m.update(str.encode(password))
    if m.hexdigest() != password_hash:
        raise HTTPException(status_code=401)
