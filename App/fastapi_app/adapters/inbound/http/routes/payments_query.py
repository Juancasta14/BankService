from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from fastapi_app.adapters.outbound.persistence.sqlalchemy.unit_of_work_pse_sqlalchemy import SqlAlchemyPSEUnitOfWork
from fastapi_app.application.pse.services.get_payment_service import GetPSEPaymentService
from fastapi_app.adapters.inbound.http.dto.pse_dto import PSETransactionOut

router = APIRouter(tags=["payments"])

def get_service(db: Session = Depends(get_db)) -> GetPSEPaymentService:
    return GetPSEPaymentService(uow=SqlAlchemyPSEUnitOfWork(db))

@router.get("/payments/{internal_order_id}")
def get_payment(internal_order_id: str, svc: GetPSEPaymentService = Depends(get_service)):
    try:
        tx = svc.get(internal_order_id)
        return PSETransactionOut.model_validate(tx)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

