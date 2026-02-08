from dataclasses import dataclass
from fastapi_app.application.pse.ports.outbound.unit_of_work import UnitOfWork

@dataclass
class GetPSEPaymentService:
    uow: UnitOfWork

    def get(self, internal_order_id: str):
        tx = self.uow.pse.get_by_internal_order_id(internal_order_id)
        if not tx:
            raise ValueError("Transacción PSE no encontrada")
        return tx
