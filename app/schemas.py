from typing import Optional
from pydantic import BaseModel, PositiveInt, constr

### Z ZAJĘĆ ###

"""
class Shipper(BaseModel):
    ShipperID: PositiveInt
    CompanyName: constr(max_length=40)
    Phone: constr(max_length=24)
    class Config:
        orm_mode = True
"""


### ZAD. 5.1 ###

class AllSuppliers(BaseModel):
    SupplierID: PositiveInt
    CompanyName: constr(max_length=40)

    class Config:
        orm_mode = True


class Supplier(BaseModel):
    SupplierID: PositiveInt
    CompanyName: Optional[constr(max_length=40)]
    ContactName: Optional[constr(max_length=30)]
    ContactTitle: Optional[constr(max_length=30)]
    Address: Optional[constr(max_length=60)]
    City: Optional[constr(max_length=15)]
    Region: Optional[constr(max_length=15)]
    PostalCode: Optional[constr(max_length=10)]
    Country: Optional[constr(max_length=15)]
    Phone: Optional[constr(max_length=24)]
    Fax: Optional[constr(max_length=24)]
    HomePage: Optional[str]

    class Config:
        orm_mode = True


### ZAD. 5.2 ###

class Category(BaseModel):
    CategoryID: Optional[int]
    CategoryName: Optional[str]

    class Config:
        orm_mode = True


class SupplierProduct(BaseModel):
    ProductID: int
    ProductName: str
    Category: Optional[Category]
    Discontinued: int

    class Config:
        orm_mode = True