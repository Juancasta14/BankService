from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from adapters.outbound.persistence.sqlalchemy.unit_of_work_pse_sqlalchemy import SqlAlchemyPSEUnitOfWork

router = APIRouter(tags=["payments"])

def get_uow(db: Session = Depends(get_db)) -> SqlAlchemyPSEUnitOfWork:
    return SqlAlchemyPSEUnitOfWork(db)

@router.get("/payments/{internal_order_id}")
def get_payment(internal_order_id: str, uow: SqlAlchemyPSEUnitOfWork = Depends(get_uow)):
    tx = uow.pse.get_by_internal_order_id(internal_order_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción PSE no encontrada")
    return tx
