from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func, update
from fastapi import HTTPException

# from . import models
import models
import schemas


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return db.query(models.Supplier)\
             .order_by(models.Supplier.SupplierID.asc())\
             .all()


def get_supplier(db: Session, id: int):
    return (
        db.query(models.Supplier)
          .filter(models.Supplier.SupplierID == id)
          .first()
    )


def get_products_from_supplier(db: Session, id: int):
    return (
        db.query(models.Product)
            .filter(models.Product.SupplierID == id)
            .order_by(models.Product.ProductID.desc())
            .all()
    )


def create_supplier(db: Session, new_supplier: schemas.NewSupplier):
    highest_id = db.query(func.max(models.Supplier.SupplierID)).scalar()
    new_supplier.SupplierID = highest_id + 1
    db.add(models.Supplier(**new_supplier.dict()))
    db.commit()
    return get_supplier(db, highest_id + 1)


def update_supplier(db: Session, id: int, supplier_update: schemas.SupplierUpdate):
    properties_to_update = {key: value for key, value in supplier_update.dict().items() if value is not None}
    update_statement = update(models.Supplier) \
                       .where(models.Supplier.SupplierID == id) \
                       .values(**properties_to_update)
    db.execute(update_statement)
    db.commit()
    return get_supplier(db, id)


def delete_supplier(db: Session, id: int):
    check_supplier = get_supplier(db, id)
    if not check_supplier:
        raise HTTPException(status_code=404)
    db.query(models.Supplier)\
      .filter(models.Supplier.SupplierID == id)\
      .delete()
    db.commit()
