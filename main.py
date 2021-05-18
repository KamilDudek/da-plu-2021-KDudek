import collections
import secrets
import datetime
import sqlite3
from datetime import timedelta, date
from typing import Optional, List

from fastapi import FastAPI, Request, Response, Query, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from hashlib import sha512, sha256

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic.main import BaseModel

from views import router as northwind_api_router

app = FastAPI()
app.counter = 0
app.patient_id = 0
app.patients_register = dict()
app.secret_key = 0
app.login_tokens = collections.deque(maxlen=3)
app.session_tokens = collections.deque(maxlen=3)
app.db_connection = None

app.include_router(northwind_api_router, tags=["northwind"])


# 1st lecture


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hello/{name}")
def hello_name_view(name: str):
    return f"Hello {name}"


@app.get("/counter")
def counter():
    app.counter += 1
    return str(app.counter)


@app.get("/method", status_code=200)
@app.put("/method", status_code=200)
@app.options("/method", status_code=200)
@app.delete("/method", status_code=200)
@app.post("/method", status_code=201)
def read_method(request: Request):
    return {"method": request.method}


class AuthResponse(BaseModel):
    status_code: int


@app.get("/auth", response_model=AuthResponse)
def authorize(response: Response, password: Optional[str] = None, password_hash: Optional[str] = None):
    response.status_code = 401
    try:
        if password and password_hash and password_hash == str(sha512(bytes(password, encoding="ASCII")).hexdigest()):
            response.status_code = 204
    except Exception:
        response.status_code = 401
    return AuthResponse(status_code=response.status_code)


class Patient(BaseModel):
    name: str
    surname: str


class RegistrationInfo(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


@app.post("/register", response_model=RegistrationInfo)
def register_patient(response: Response, patient: Patient):
    app.patient_id += 1
    how_many_days = sum(character.isalpha() for character in patient.name) \
                    + sum(character.isalpha() for character in patient.surname)
    registration_date = date.today()
    vaccination_date = registration_date + timedelta(days=how_many_days)
    response.status_code = 201
    app.patients_register[app.patient_id] = RegistrationInfo(
        id=app.patient_id,
        name=patient.name,
        surname=patient.surname,
        register_date=registration_date.strftime("%Y-%m-%d"),
        vaccination_date=vaccination_date.strftime("%Y-%m-%d")
    )
    return app.patients_register[app.patient_id]


@app.get("/patient/{id}", response_model=Optional[RegistrationInfo])
def get_patient(response: Response, id: int):
    if id < 1:
        response.status_code = 400
    elif id not in app.patients_register:
        response.status_code = 404
    else:
        response.status_code = 200
        return app.patients_register[id]


# 3rd lecture


@app.get("/hello", response_class=HTMLResponse)
def hello():
    today = date.today()
    return f"""
    <html>
        <body>
            <h1>Hello! Today date is {today.strftime("%Y-%m-%d")}</h1>
        </body>
    </html>
    """


security = HTTPBasic()


@app.post("/login_session")
def create_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    response.status_code = 401
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if correct_username and correct_password:
        response.status_code = 201
        session_token = sha256(f"4dm1nNotSoSecurePa$${app.secret_key}".encode()).hexdigest()
        app.session_tokens.append(session_token)
        response.set_cookie(key="session_token", value=session_token)
        app.secret_key += 1


@app.post("/login_token")
def check_token(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    response.status_code = 401
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if correct_username and correct_password:
        response.status_code = 201
        token = sha256(f"4dm1nNotSoSecurePa$${app.secret_key}".encode()).hexdigest()
        app.login_tokens.append(token)
        app.secret_key += 1
        return {"token": token}


@app.get("/welcome_session")
def welcome_session(response: Response, format: Optional[str] = None, session_token: str = Cookie(None)):
    response.status_code = 401
    if session_token in app.session_tokens:
        return return_message(text="Welcome!", message_format=format)


@app.get("/welcome_token")
def welcome_token(response: Response, token: str, format: Optional[str] = None):
    response.status_code = 401
    if token in app.login_tokens:
        return return_message(text="Welcome!", message_format=format)


def return_message(text: str, message_format: Optional[str]):
    if message_format == "json":
        return JSONResponse(content={"message": text}, status_code=200)
    if message_format == "html":
        return HTMLResponse(content=f"<html><h1>{text}</h1></html>", status_code=200)
    return PlainTextResponse(content=text, status_code=200)


@app.delete("/logout_session")
def logout_session(response: Response, format: Optional[str] = None, session_token: str = Cookie(None)):
    response.status_code = 401
    if session_token in app.session_tokens:
        app.session_tokens.remove(session_token)
        return RedirectResponse(url="/logged_out" + f"?format={format}", status_code=303)


@app.delete("/logout_token")
def logout_token(response: Response, token: str, format: Optional[str] = None):
    response.status_code = 401
    if token in app.login_tokens:
        app.login_tokens.remove(token)
        return RedirectResponse(url="/logged_out" + f"?format={format}", status_code=303)


@app.get("/logged_out")
def logged_out(format: Optional[str] = None):
    return return_message(text="Logged out!", message_format=format)


# 4th lecture

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/categories", status_code=200)
async def print_categories():
    cursor = app.db_connection.cursor()
    cursor.row_factory = lambda cursor, col: {"id": col[0], "name": col[1]}
    result = cursor.execute("SELECT CategoryID, CategoryName FROM Categories").fetchall()
    return {"categories": result}


def xstr(s):
    if s is None:
        return ''
    return str(s)


@app.get("/customers", status_code=200)
async def print_customers():
    cursor = app.db_connection.cursor()
    cursor.row_factory = lambda cursor, col: {"id": col[0],
                                              "name": col[1],
                                              "full_address": xstr(col[2]) + " "
                                                              + xstr(col[3]) + " "
                                                              + xstr(col[4]) + " "
                                                              + xstr(col[5])}
    result = cursor.execute('''SELECT CustomerID, CompanyName, Address, PostalCode, City, Country 
                                FROM Customers''').fetchall()
    return {"customers": result}


@app.get("/products/{id}")
async def get_product(response: Response, id: int):
    response.status_code = 404
    cursor = app.db_connection.cursor()
    cursor.row_factory = lambda cursor, col: {"id": col[0], "name": col[1]}
    result = cursor.execute("SELECT ProductID, ProductName FROM Products WHERE ProductID = :id",
                            {"id": id}).fetchone()
    if result is not None:
        response.status_code = 200
        return result


@app.get("/employees")
async def get_employees(response: Response, limit: Optional[int] = -1, offset: Optional[int] = 0,
                        order: Optional[str] = None):
    response.status_code = 200
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    order_by = ['first_name', 'last_name', 'city']
    if not any(order == possibility for possibility in order_by) and order is not None:
        response.status_code = 400
        return
    if order is None:
        order = 'EmployeeID'
    result = cursor.execute(f"""SELECT EmployeeID id, LastName last_name, FirstName first_name, City city 
                            FROM Employees e 
                            ORDER BY {order} 
                            LIMIT :limit 
                            OFFSET :offset""",
                            {'limit': limit, 'offset': offset}).fetchall()
    return {"employees": result}


@app.get("/products_extended")
async def products_extended(response: Response):
    response.status_code = 200
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    result = cursor.execute(
        '''SELECT p.ProductID id, p.ProductName name, c.CategoryName category, s.CompanyName supplier
           FROM Products p 
           JOIN Categories c ON p.CategoryID = c.CategoryID 
           JOIN Suppliers s ON p.SupplierID = s.SupplierID''').fetchall()
    return {"products_extended": result}


@app.get("/products/{id}/orders")
async def order_details(response: Response, id: int):
    response.status_code = 200
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    result = cursor.execute(
        '''SELECT o.OrderID id, c.CompanyName customer, 
	              od.Quantity quantity,
	              ROUND((od.UnitPrice * od.Quantity) - od.Discount * (od.UnitPrice * od.Quantity),2) total_price
           FROM Orders o 
	              JOIN Customers c ON o.CustomerID = c.CustomerID 
	              JOIN "Order Details" od ON o.OrderID = od.OrderID	
           WHERE od.ProductID = :id
        ''', {"id": id}).fetchall()
    if result:
        return {"orders": result}
    raise HTTPException(status_code=404)


class Category(BaseModel):
    name: str


class CreatedCategory(BaseModel):
    id: int
    name: str


@app.post("/categories", status_code=201, response_model=CreatedCategory)
async def create_category(category: Category):
    cursor = app.db_connection.execute(
        "INSERT INTO Categories (CategoryName) VALUES (?)", (category.name, ))
    app.db_connection.commit()
    return {"id": cursor.lastrowid,
            "name": category.name}


@app.put("/categories/{id}", status_code=200, response_model=CreatedCategory)
async def modify_category(category: Category, id: int):
    cursor = app.db_connection.execute(
        "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?", (category.name, id)
    )
    app.db_connection.commit()
    cursor.row_factory = sqlite3.Row
    created_category = cursor.execute(
        '''SELECT c.CategoryID id, c.CategoryName name 
            FROM Categories c 
            WHERE c.CategoryID = :id''', {"id": id}).fetchone()
    if created_category:
        return created_category
    raise HTTPException(status_code=404)


@app.delete("/categories/{id}", status_code=200)
async def delete_category(id: int):
    cursor = app.db_connection.execute(
        '''SELECT c.CategoryID 
            FROM Categories c 
            WHERE c.CategoryID = :id''', {'id': id})
    if not cursor.fetchone():
        raise HTTPException(status_code=404)
    cursor.execute(
        '''DELETE FROM Categories 
            WHERE categoryID = :id''', {"id": id})
    app.db_connection.commit()
    return {"deleted": 1}
