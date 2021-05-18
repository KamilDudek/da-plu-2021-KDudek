from sqlalchemy.orm import Session

from . import models

### Z ZAJĘĆ ###

"""
def get_shippers(db: Session):
    return db.query(models.Shipper).all()
def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )
"""

### ZAD. 5.1 ###

def get_all_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID).all()

def get_supplier(db: Session, supplier_id: int):
    return(db.query(models.Supplier).filter(
        models.Supplier.SupplierID == supplier_id).first())

### ZAD. 5.2 ###

def get_supplier_products(db: Session, supplier_id:int):
    return db.query(models.Product).filter(
        models.Product.SupplierID == supplier_id).order_by(
        models.Product.ProductID.desc()).all()
    #return db.query(models.Product).join(models.Category).all()