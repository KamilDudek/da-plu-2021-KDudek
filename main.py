from fastapi import FastAPI, HTTPException, Response, Request
from datetime import datetime, timedelta

import hashlib

app = FastAPI()
app.counter = 0
app.patients_table = []


@app.get("/", status_code=200)
def root():
    return {"message": "Hello World"}


@app.get("/method", status_code=200)
async def check_method():
    return {"method": "GET"}


@app.get("/auth", response_class=Response, status_code=204)
async def auth_method(password: str, password_hash: str):
    m = hashlib.sha512()
    m.update(str.encode(password))
    if m.hexdigest() != password_hash:
        raise HTTPException(status_code=401)


@app.post('/register')
async def register_post(request: Request):
    register_data = await request.json()
    name_len = len(register_data['name'])
    surname_len = len(register_data['surname'])
    app.counter += 1
    register_data['id'] = app.counter
    today = datetime.now()
    register_data['date'] = today.strftime("%Y-%m-%d")
    x = today + timedelta(days=surname_len + name_len)
    register_data['vaccination_date'] = x.strftime("%Y-%m-%d")
    z = list(register_data.items())
    order = [2, 0, 1, 3, 4]
    z = [z[i] for i in order]
    register_data = dict(z)

    app.patients_table.append(register_data)

    return register_data


@app.get('/patient/{id}')
async def get_patient_by_id(id: int):
    for patient_dict in app.patients_table:
        for key, value in patient_dict.items():
            if key == 'id' and value == id:
                return patient_dict
