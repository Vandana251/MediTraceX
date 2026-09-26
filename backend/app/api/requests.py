"""
Medicine Procurement Requests API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.request_schemas import (
    MedicineRequestCreate,
    MedicineRequestStatusUpdate,
    MedicineRequestResponse
)
from database.models import User, MedicineRequest, Medicine, Pharmacy

router = APIRouter(prefix="/requests", tags=["Medicine Requests"])

def _format_request_response(req: MedicineRequest) -> MedicineRequestResponse:
    return MedicineRequestResponse(
        id=req.id,
        user_id=req.user_id,
        user_name=req.user.name if req.user else None,
        user_phone=req.user.phone if req.user else None,
        pharmacy_id=req.pharmacy_id,
        pharmacy_name=req.pharmacy.name if req.pharmacy else None,
        medicine_id=req.medicine_id,
        medicine_name=req.medicine.name if req.medicine else None,
        quantity_requested=req.quantity_requested,
        status=req.status,
        notes=req.notes,
        created_at=req.created_at,
        updated_at=req.updated_at
    )

@router.post("", response_model=MedicineRequestResponse, status_code=status.HTTP_201_CREATED, summary="Create a new medicine procurement request")
def create_medicine_request(
    payload: MedicineRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    medicine = db.query(Medicine).filter(Medicine.id == payload.medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {payload.medicine_id} not found."
        )

    if payload.pharmacy_id:
        pharmacy = db.query(Pharmacy).filter(Pharmacy.id == payload.pharmacy_id).first()
        if not pharmacy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target pharmacy with ID {payload.pharmacy_id} not found."
            )

    new_req = MedicineRequest(
        user_id=current_user.id,
        pharmacy_id=payload.pharmacy_id,
        medicine_id=payload.medicine_id,
        quantity_requested=payload.quantity_requested,
        status="PENDING",
        notes=payload.notes
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return _format_request_response(new_req)

@router.get("/my", response_model=List[MedicineRequestResponse], summary="Get all medicine requests created by current user")
def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    requests = (
        db.query(MedicineRequest)
        .filter(MedicineRequest.user_id == current_user.id)
        .order_by(MedicineRequest.created_at.desc())
        .all()
    )
    return [_format_request_response(r) for r in requests]

@router.get("/pharmacy", response_model=List[MedicineRequestResponse], summary="Get incoming requests for pharmacy (Pharmacy Role)")
def get_pharmacy_incoming_requests(
    current_user: User = Depends(require_roles(["pharmacy_admin", "pharmacy", "system_admin"])),
    db: Session = Depends(get_db)
) -> Any:
    # If system admin, return all; if pharmacy admin, return assigned or broadcast requests
    requests = (
        db.query(MedicineRequest)
        .order_by(MedicineRequest.created_at.desc())
        .all()
    )
    return [_format_request_response(r) for r in requests]

@router.get("/{request_id}", response_model=MedicineRequestResponse, summary="Get details of a specific medicine request")
def get_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    req = db.query(MedicineRequest).filter(MedicineRequest.id == request_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine request with ID {request_id} not found."
        )

    # Access check: user owns it or user is pharmacy admin / sysadmin
    if req.user_id != current_user.id and current_user.role not in ["pharmacy_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view this request."
        )

    return _format_request_response(req)

@router.put("/{request_id}/status", response_model=MedicineRequestResponse, summary="Update medicine request status (Pharmacy Role)")
def update_request_status(
    request_id: int,
    payload: MedicineRequestStatusUpdate,
    current_user: User = Depends(require_roles(["pharmacy_admin", "pharmacy", "system_admin"])),
    db: Session = Depends(get_db)
) -> Any:
    valid_statuses = ["PENDING", "ACCEPTED", "FULFILLED", "CANCELLED", "NOT_AVAILABLE"]
    norm_status = payload.status.upper().strip()
    if norm_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Allowed values: {valid_statuses}"
        )

    req = db.query(MedicineRequest).filter(MedicineRequest.id == request_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine request with ID {request_id} not found."
        )

    req.status = norm_status
    req.updated_at = datetime.now()
    db.commit()
    db.refresh(req)

    return _format_request_response(req)
