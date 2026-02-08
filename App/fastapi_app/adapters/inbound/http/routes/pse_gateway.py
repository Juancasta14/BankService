from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db

from fastapi_app.adapters.outbound.persistence.sqlalchemy.unit_of_work_pse_sqlalchemy import (
    SqlAlchemyPSEUnitOfWork,
)
from fastapi_app.application.pse.services.process_gateway_service import (
    ProcessPSEGatewayService,
)

router = APIRouter(tags=["pse-gateway"])

def get_gateway_service(db: Session = Depends(get_db)) -> ProcessPSEGatewayService:
    uow = SqlAlchemyPSEUnitOfWork(db)
    return ProcessPSEGatewayService(uow=uow)

@router.get("/pse-gateway/{internal_order_id}")
def pse_gateway(
    internal_order_id: str,
    svc: ProcessPSEGatewayService = Depends(get_gateway_service),
):
    try:
        result, redirect_url = svc.process(internal_order_id)
        return RedirectResponse(url=redirect_url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno PSE gateway: {e}")
