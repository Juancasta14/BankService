from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from fastapi_app.adapters.outbound.persistence.sqlalchemy.unit_of_work_sqlalchemy import SqlAlchemyUnitOfWork
from fastapi_app.application.banking.services.transfer_service import TransferService
from fastapi_app..adapters.inbound.http.dto.transfer_dto import TransferRequest

from fastapi_app..domain.banking.exceptions import (
    InvalidAmount, SameAccount, AccountNotFound, InsufficientFunds
)

router = APIRouter(tags=["transfers"])

def get_transfer_service(db: Session = Depends(get_db)) -> TransferService:
    uow = SqlAlchemyUnitOfWork(db)
    return TransferService(uow=uow)

@router.post("/customers/{customer_id}/transfer")
def make_transfer(customer_id: int, req: TransferRequest, svc: TransferService = Depends(get_transfer_service)):
    try:
        svc.transfer(req.from_account_id, req.to_account_id, req.amount)
        return {"message": "Transferencia realizada correctamente"}
    except (InvalidAmount, SameAccount) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientFunds as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # si algo falla, rollback
        # (si quieres: expón rollback dentro del service con try/except)
        raise HTTPException(status_code=500, detail=f"Error interno al procesar la transferencia: {e}")
