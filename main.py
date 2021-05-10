import sqlite3

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from typing import List

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(
        errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/products")
async def products():
    products = app.db_connection.execute(
        "SELECT ProductName FROM Products").fetchall()
    return {
        "products": products,
        "products_counter": len(products)
    }


@app.get("/suppliers/{supplier_id}")
async def single_supplier(supplier_id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT CompanyName, Address FROM Suppliers WHERE SupplierID = :supplier_id",
        {'supplier_id': supplier_id}).fetchone()

    return data


@app.get("/employee_with_region")
async def employee_with_region():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
        SELECT Employees.LastName, Employees.FirstName, Territories.TerritoryDescription 
        FROM Employees JOIN EmployeeTerritories ON Employees.EmployeeID = EmployeeTerritories.EmployeeID
        JOIN Territories ON EmployeeTerritories.TerritoryID = Territories.TerritoryID;
     ''').fetchall()
    return [{"employee": f"{x['FirstName']} {x['LastName']}",
             "region": x["TerritoryDescription"]} for x in data]


@app.get("/customers")
async def customers():
    app.db_connection.row_factory = lambda cursor, x: x[0]
    artists = app.db_connection.execute(
        "SELECT CompanyName FROM Customers").fetchall()
    return artists


class Customer(BaseModel):
    company_name: str


@app.post("/customers/add")
async def customers_add(customer: Customer):
    cursor = app.db_connection.execute(
        f"INSERT INTO Customers (CompanyName) VALUES ('{customer.company_name}')"
    )
    app.db_connection.commit()
    return {
        "CustomerID": cursor.lastrowid,
        "CompanyName": customer.company_name
    }


class Shipper(BaseModel):
    company_name: str


@app.patch("/shippers/edit/{shipper_id}")
async def artists_add(shipper_id: int, shipper: Shipper):
    cursor = app.db_connection.execute(
        "UPDATE Shippers SET CompanyName = ? WHERE ShipperID = ?", (
            shipper.company_name, shipper_id)
    )
    app.db_connection.commit()

    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        """SELECT ShipperID AS shipper_id, CompanyName AS company_name
         FROM Shippers WHERE ShipperID = ?""",
        (shipper_id,)).fetchone()

    return data


@app.get("/orders")
async def orders():
    app.db_connection.row_factory = sqlite3.Row
    orders = app.db_connection.execute("SELECT * FROM Orders").fetchall()
    return {
        "orders_counter": len(orders),
        "orders": orders,
    }


@app.delete("/orders/delete/{order_id}")
async def order_delete(order_id: int):
    cursor = app.db_connection.execute(
        "DELETE FROM Orders WHERE OrderID = ?", (order_id,)
    )
    app.db_connection.commit()
    return {"deleted": cursor.rowcount}


@app.get("/region_count")
async def root():
    app.db_connection.row_factory = lambda cursor, x: x[0]
    regions = app.db_connection.execute(
        "SELECT RegionDescription FROM Regions ORDER BY RegionDescription DESC").fetchall()
    count = app.db_connection.execute(
        'SELECT COUNT(*) FROM Regions').fetchone()

    return {
        "regions": regions,
        "regions_counter": count
    }


# task1
@app.get("/categories", status_code=200)
async def categores():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
    SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID
    ''').fetchall()
    return {"categories": [{"id": x['CategoryID'], "name": x["CategoryName"]} for x in data]}

@app.get("/customers", status_code=200)
async def customers():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
    SELECT CustomerID, CompanyName, (COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || COALESCE(City, '') || ' ' || COALESCE(Country, '')) AS full_address FROM Customers ORDER BY CustomerID
    ''').fetchall()
    return {"customers": [{"id": f"{x['CustomerID']}", "name": x["CompanyName"], "full_address": (x["full_address"])} for x in data]}

# taks2
@app.get("/products/{id}")
async def products_by_id(id: int):
    app.db_connection.row_factory = sqlite3.Row
    products = app.db_connection.execute(
        f"SELECT ProductName FROM Products WHERE ProductID={id} ").fetchone()
    if products != None:
        product = {"id": id, "name": products['ProductName']}
        return product
    else:
        raise HTTPException(status_code=404, detail="ID doesn't exist")

#task3
@app.get('/employees', status_code=200)
async def employees(limit: int = -1, offset: int = 0, order: str = 'id'):
    app.db_connection.row_factory = sqlite3.Row
    columns = {'first_name' : 'FirstName', 'last_name' : 'LastName', 'city' : 'City', 'id' : 'EmployeeID'}
    if order not in columns.keys():
        raise HTTPException(status_code=400)
    order = columns[order]
    data = app.db_connection.execute(f"SELECT EmployeeID, LastName, FirstName, City FROM Employees ORDER BY {order} LIMIT ? OFFSET ?",(limit, offset, )).fetchall()
    return {"employees": [{"id": x['EmployeeID'],"last_name":x['LastName'],"first_name":x['FirstName'],"city":x['City']} for x in data]}

#task4
@app.get('/products_extended', status_code=200)
async def products_extended():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
    SELECT Products.ProductID AS id, Products.ProductName AS name, Categories.CategoryName AS category, Suppliers.CompanyName AS supplier FROM Products 
    JOIN Categories ON Products.CategoryID = Categories.CategoryID JOIN Suppliers ON Products.SupplierID = Suppliers.SupplierID ORDER BY Products.ProductID
    ''').fetchall()
    return {"products_extended": [{"id": x['id'], "name": x['name'], "category": x['category'], "supplier": x['supplier']} for x in data]}

#task5
@app.get('/products/{id}/orders', status_code=200)
async def products_id_orders(id: int):
    app.db_connection.row_factory = sqlite3.Row # (UnitPrice x Quantity) - (Discount x (UnitPrice x Quantity))
    data = app.db_connection.execute(f'''
    SELECT Products.ProductID, Orders.OrderID AS id, Customers.CompanyName AS customer, [Order Details].Quantity AS quantity, [Order Details].UnitPrice AS unitprice, [Order Details].Discount as discount 
    FROM Products JOIN [Order Details] ON Products.ProductID = [Order Details].ProductID JOIN Orders ON [Order Details].OrderID = Orders.OrderID JOIN Customers ON Orders.CustomerID = Customers.CustomerID WHERE Products.ProductID = {id} ORDER BY Orders.OrderID
    ''').fetchall()
    if data == []:
        raise HTTPException(status_code=404) #
    return {"orders": [{"id": x["id"], "customer": x["customer"], "quantity": x["quantity"], "total_price": round(((x['unitprice'] * x['quantity']) - (x['discount'] * (x['unitprice'] * x['quantity']))), 2)} for x in data]}