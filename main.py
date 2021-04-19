from fastapi import FastAPI, HTTPException, responses
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
import re
from typing import Optional
from pydantic import BaseModel
import hashlib

app = FastAPI()
app.counter = 0
app.patients_table = []


class Patient(BaseModel):
    name: str
    surname: str


@app.get("/", status_code=200)
async def root():
    return {"message": "Hello world!"}


@app.get("/method", status_code=200)
async def check_method_get():
    return {"method": "GET"}


@app.put("/method", status_code=200)
async def check_method_put():
    return {"method": "PUT"}


@app.delete("/method", status_code=200)
async def check_method_delete():
    return {"method": "DELETE"}


@app.options("/method", status_code=200)
async def check_method_options():
    return {"method": "OPTIONS"}


@app.post("/method", status_code=201)
async def check_method_post():
    return {"method": "POST"}


@app.get("/auth", status_code=204)
async def auth_method(password: Optional[str] = None,
                      password_hash: Optional[str] = None):
    m = hashlib.sha512()
    m.update(str.encode(password))
    if m.hexdigest() != password_hash or not password or not password_hash:
        raise HTTPException(status_code=401)


@app.post('/register', status_code=201)
async def register_post(patient: Patient):
    register_data = jsonable_encoder(patient)
    name_len = len("".join(re.findall("[a-zA-z+]", register_data['name'])))
    surname_len = len(
        "".join(re.findall("[a-zA-z+]", register_data['surname'])))

    if name_len == 0 or surname_len == 0:
        raise HTTPException(status_code=422)
    app.counter += 1
    register_data['id'] = app.counter
    today = datetime.now()
    register_data['register_date'] = today.strftime("%Y-%m-%d")
    vaccination_date = today + timedelta(days=surname_len + name_len)
    register_data['vaccination_date'] = vaccination_date.strftime("%Y-%m-%d")
    register_data_list = list(register_data.items())
    order = [2, 0, 1, 3, 4]
    register_data_list = [register_data_list[i] for i in order]
    register_data = dict(register_data_list)
    app.patients_table.append(register_data)

    return register_data


@app.get('/patient/{id}', status_code=200)
async def get_patient_by_id(id: int):
    if id < 1:
        raise HTTPException(status_code=400)

    for patient_dict in app.patients_table:
        for key, value in patient_dict.items():
            if key == 'id' and value == id:
                return patient_dict

    raise HTTPException(status_code=404)
