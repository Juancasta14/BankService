from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from adapters.outbound.persistence.sqlalchemy.unit_of_work_pse_sqlalchemy import SqlAlchemyPSEUnitOfWork
from application.pse.services.create_payment_service import CreatePSEPaymentService
from fastapi.adapters.inbound.http.dto import PSETransactionCreate



router = APIRouter(tags=["pse-payments"])

def get_create_payment_service(db: Session = Depends(get_db)) -> CreatePSEPaymentService:
    uow = SqlAlchemyPSEUnitOfWork(db)
    return CreatePSEPaymentService(uow=uow)

@router.post("/payments")
def create_payment(data: PSETransactionCreate, svc: CreatePSEPaymentService = Depends(get_create_payment_service)):
    try:
        return svc.create_payment(
            customer_id=data.customer_id,
            account_id=data.account_id,
            amount=data.amount,
            currency=data.currency,
            return_url_success=data.return_url_success,
            return_url_failure=data.return_url_failure,
        )
    except ValueError as e:
        msg = str(e)
        if "no encontrada" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "Saldo insuficiente" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al crear la orden PSE: {e}")
