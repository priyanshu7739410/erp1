from sqlalchemy.orm import Session
from app.models.inventory import InventoryItem, StockTransaction, Prescription, PurchaseOrder
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    StockTransactionCreate,
    PrescriptionCreate,
    PurchaseOrderCreate
)
from app.utils.exceptions import NotFoundException, ConflictException, BadRequestException
from app.utils.pagination import paginate

def create_item(db: Session, data: InventoryItemCreate) -> InventoryItem:
    existing = db.query(InventoryItem).filter(InventoryItem.sku == data.sku).first()
    if existing:
        raise ConflictException(detail="Item with this SKU already exists")
    item = InventoryItem(**data.model_dump(), is_active=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_item(db: Session, item_id: int) -> InventoryItem:
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise NotFoundException(detail="Inventory item not found")
    return item

def list_items(db: Session, category: str = None, reorder_only: bool = False, page: int = 1, size: int = 10) -> dict:
    query = db.query(InventoryItem).filter(InventoryItem.is_active == True)
    if category:
        query = query.filter(InventoryItem.category == category)
    if reorder_only:
        query = query.filter(InventoryItem.quantity <= InventoryItem.reorder_level)
    return paginate(query.order_by(InventoryItem.name), page, size)

def update_item(db: Session, item_id: int, data: InventoryItemUpdate) -> InventoryItem:
    item = get_item(db, item_id)
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

def record_transaction(db: Session, data: StockTransactionCreate) -> StockTransaction:
    item = get_item(db, data.item_id)
    if data.transaction_type == "out" and item.quantity < abs(data.quantity_change):
        raise BadRequestException(detail=f"Insufficient stock for {item.name}. Available: {item.quantity}")
        
    change = data.quantity_change
    if data.transaction_type == "out" and change > 0:
        change = -change
    elif data.transaction_type == "in" and change < 0:
        change = abs(change)
        
    item.quantity += change
    if item.quantity < 0:
        item.quantity = 0

    tx = StockTransaction(
        item_id=data.item_id,
        quantity_change=change,
        transaction_type=data.transaction_type,
        notes=data.notes,
        recorded_by=data.recorded_by
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def list_transactions(db: Session, item_id: int = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(StockTransaction)
    if item_id is not None:
        query = query.filter(StockTransaction.item_id == item_id)
    return paginate(query.order_by(StockTransaction.date.desc()), page, size)

def create_prescription(db: Session, data: PrescriptionCreate) -> Prescription:
    pres = Prescription(**data.model_dump(), status="active")
    db.add(pres)
    db.commit()
    db.refresh(pres)
    return pres

def dispense_prescription(db: Session, pres_id: int, dispensed_by: str) -> Prescription:
    pres = db.query(Prescription).filter(Prescription.id == pres_id).first()
    if not pres:
        raise NotFoundException(detail="Prescription not found")
    if pres.status == "dispensed":
        raise BadRequestException(detail="Prescription already dispensed")

    # Match medication name to inventory item
    item = db.query(InventoryItem).filter(InventoryItem.name.ilike(f"%{pres.medication_name}%"), InventoryItem.is_active == True).first()
    if item:
        required_qty = pres.duration_days # simple assumption: 1 unit per day
        if item.quantity < required_qty:
            raise BadRequestException(detail=f"Insufficient stock to dispense {pres.medication_name}. Stock: {item.quantity}")
        
        # Record stock transaction
        record_transaction(db, StockTransactionCreate(
            item_id=item.id,
            quantity_change=-required_qty,
            transaction_type="out",
            notes=f"Dispensed for prescription ID {pres.id}",
            recorded_by=dispensed_by
        ))
        
    pres.status = "dispensed"
    db.commit()
    db.refresh(pres)
    return pres

def list_prescriptions(db: Session, patient_id: int = None, status: str = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(Prescription)
    if patient_id is not None:
        query = query.filter(Prescription.patient_id == patient_id)
    if status:
        query = query.filter(Prescription.status == status)
    return paginate(query.order_by(Prescription.created_at.desc()), page, size)

def create_purchase_order(db: Session, data: PurchaseOrderCreate) -> PurchaseOrder:
    po = PurchaseOrder(**data.model_dump(), status="ordered")
    db.add(po)
    db.commit()
    db.refresh(po)
    return po

def receive_purchase_order(db: Session, po_id: int, received_by: str) -> PurchaseOrder:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise NotFoundException(detail="Purchase order not found")
    if po.status == "received":
        raise BadRequestException(detail="Purchase order already received")
        
    po.status = "received"
    record_transaction(db, StockTransactionCreate(
        item_id=po.item_id,
        quantity_change=po.quantity,
        transaction_type="in",
        notes=f"Received PO #{po.id}",
        recorded_by=received_by
    ))
    db.commit()
    db.refresh(po)
    return po

def list_purchase_orders(db: Session, status: str = None, page: int = 1, size: int = 10) -> dict:
    query = db.query(PurchaseOrder)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    return paginate(query.order_by(PurchaseOrder.order_date.desc()), page, size)
