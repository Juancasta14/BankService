from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from adapters.outbound.persistence.sqlalchemy.unit_of_work_pse_sqlalchemy import SqlAlchemyPSEUnitOfWork
from application.pse.services.process_callback_service import ProcessPSECallbackService
from adapters.inbound.http.dto.pse_dto import PSECallbackIn
 

router = APIRouter(tags=["pse-callback"])

def get_callback_service(db: Session = Depends(get_db)) -> ProcessPSECallbackService:
    uow = SqlAlchemyPSEUnitOfWork(db)
    return ProcessPSECallbackService(uow=uow)

@router.post("/callback")
def callback(data: PSECallbackIn, svc: ProcessPSECallbackService = Depends(get_callback_service)):
    try:
        return svc.process_callback(
            internal_order_id=data.internal_order_id,
            status=data.status,
            provider_tx_id=data.provider_tx_id,
            provider_reference=data.provider_reference,
            raw_payload=data.raw_payload,
        )
    except ValueError as e:
        msg = str(e)
        if "no encontrada" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al procesar callback: {e}")
