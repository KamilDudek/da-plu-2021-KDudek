from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import PositiveInt
from sqlalchemy.orm import Session

# from . import crud, schemas
# from .database import get_db
import crud
import database
import schemas

router = APIRouter()


@router.get("/shippers/{shipper_id}", response_model=schemas.Shipper)
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(database.get_db)):
    db_shipper = crud.get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@router.get("/shippers", response_model=List[schemas.Shipper])
async def get_shippers(db: Session = Depends(database.get_db)):
    return crud.get_shippers(db)


# lecture 5

@router.get("/suppliers", response_model=List[schemas.SupplierSimplified])
async def get_suppliers(db: Session = Depends(database.get_db)):
    return crud.get_suppliers(db)


@router.get("/suppliers/{id}", response_model=schemas.Supplier)
async def get_supplier(id: PositiveInt, db: Session = Depends(database.get_db)):
    db_supplier = crud.get_supplier(db, id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier


@router.get("/suppliers/{id}/products", response_model=List[schemas.ProductFromSupplier])
async def get_products_from_supplier(id: PositiveInt, db: Session = Depends(database.get_db)):
    db_products_from_supplier = crud.get_products_from_supplier(db, id)
    if not db_products_from_supplier:
        raise HTTPException(status_code=404)
    return db_products_from_supplier


@router.post("/suppliers", response_model=schemas.Supplier, status_code=201)
async def create_supplier(new_supplier: schemas.NewSupplier, db: Session = Depends(database.get_db)):
    return crud.create_supplier(db, new_supplier)


@router.put("/suppliers/{id}", response_model=schemas.Supplier)
async def update_supplier(id: int, supplier_update: schemas.SupplierUpdate, db: Session = Depends(database.get_db)):
    updated_supplier = crud.update_supplier(db, id, supplier_update)
    if not updated_supplier:
        raise HTTPException(status_code=404)
    return updated_supplier


@router.delete("/suppliers/{id}", status_code=204)
async def delete_supplier(id: int, db: Session = Depends(database.get_db)):
    crud.delete_supplier(db, id)
