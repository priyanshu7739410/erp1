from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    StockTransactionCreate,
    StockTransactionResponse,
    PrescriptionCreate,
    PrescriptionResponse,
    PurchaseOrderCreate,
    PurchaseOrderResponse
)
from app.services.inventory_service import (
    create_item,
    get_item,
    list_items,
    update_item,
    record_transaction,
    list_transactions,
    create_prescription,
    dispense_prescription,
    list_prescriptions,
    create_purchase_order,
    receive_purchase_order,
    list_purchase_orders
)
from app.auth.dependencies import RoleChecker, get_current_active_user
from app.models.user import User
from app.utils.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory & Pharmacy"])
allow_staff = RoleChecker(["admin", "pharmacist", "doctor", "nurse"])
require_pharma = RoleChecker(["admin", "pharmacist"])

@router.post("/items", response_model=InventoryItemResponse, dependencies=[Depends(require_pharma)])
def add_inventory_item(data: InventoryItemCreate, db: Session = Depends(get_db)):
    return create_item(db, data)

@router.get("/items", response_model=PaginatedResponse[InventoryItemResponse], dependencies=[Depends(allow_staff)])
def get_inventory_items(
    category: Optional[str] = None,
    reorder_only: bool = False,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_items(db, category=category, reorder_only=reorder_only, page=page, size=size)

@router.get("/items/{item_id}", response_model=InventoryItemResponse, dependencies=[Depends(allow_staff)])
def get_single_item(item_id: int, db: Session = Depends(get_db)):
    return get_item(db, item_id)

@router.put("/items/{item_id}", response_model=InventoryItemResponse, dependencies=[Depends(require_pharma)])
def modify_item(item_id: int, data: InventoryItemUpdate, db: Session = Depends(get_db)):
    return update_item(db, item_id, data)

@router.post("/transactions", response_model=StockTransactionResponse)
def add_transaction(
    data: StockTransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_pharma)
):
    return record_transaction(db, data)

@router.get("/transactions", response_model=PaginatedResponse[StockTransactionResponse], dependencies=[Depends(allow_staff)])
def get_stock_transactions(
    item_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_transactions(db, item_id=item_id, page=page, size=size)

@router.post("/prescriptions", response_model=PrescriptionResponse, dependencies=[Depends(RoleChecker(["admin", "doctor"]))])
def add_prescription(data: PrescriptionCreate, db: Session = Depends(get_db)):
    return create_prescription(db, data)

@router.post("/prescriptions/{pres_id}/dispense", response_model=PrescriptionResponse)
def dispense_medication(
    pres_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_pharma)
):
    return dispense_prescription(db, pres_id, dispensed_by=user.username)

@router.get("/prescriptions", response_model=PaginatedResponse[PrescriptionResponse], dependencies=[Depends(allow_staff)])
def get_all_prescriptions(
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_prescriptions(db, patient_id=patient_id, status=status, page=page, size=size)

@router.post("/purchase-orders", response_model=PurchaseOrderResponse, dependencies=[Depends(require_pharma)])
def add_purchase_order(data: PurchaseOrderCreate, db: Session = Depends(get_db)):
    return create_purchase_order(db, data)

@router.post("/purchase-orders/{po_id}/receive", response_model=PurchaseOrderResponse)
def receive_order(
    po_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_pharma)
):
    return receive_purchase_order(db, po_id, received_by=user.username)

@router.get("/purchase-orders", response_model=PaginatedResponse[PurchaseOrderResponse], dependencies=[Depends(require_pharma)])
def get_purchase_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_purchase_orders(db, status=status, page=page, size=size)
