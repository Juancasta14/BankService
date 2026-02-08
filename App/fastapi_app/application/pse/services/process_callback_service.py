from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProcessPSECallbackService:
    uow: any  # SqlAlchemyPSEUnitOfWork

    def process_callback(
        self,
        *,
        internal_order_id: str,
        status: str,
        provider_tx_id: str | None,
        provider_reference: str | None,
        raw_payload: dict | None,
    ) -> dict:
        tx = self.uow.pse.get_by_internal_order_id(internal_order_id)
        if not tx:
            raise ValueError("Transacción PSE no encontrada")

        # Actualizar datos del proveedor (siempre)
        tx.status = status
        tx.provider_tx_id = provider_tx_id
        tx.provider_reference = provider_reference
        tx.callback_status_raw = self.uow.pse.serialize_payload(raw_payload)
        tx.updated_at = datetime.utcnow()

        # Si éxito, acreditar cuenta + movimiento
        if status.upper() == "SUCCESS":
            account = self.uow.accounts.get(tx.account_id)
            if not account:
                raise ValueError("Cuenta asociada no existe")

            account.balance += tx.amount

            today = datetime.utcnow().strftime("%Y-%m-%d")
            self.uow.movements.add_credit(
                account_id=account.id,
                customer_id=account.customer_id,
                account_type=account.type,
                date=today,
                description=f"Depósito vía PSE ref {tx.internal_order_id}",
                amount=tx.amount,
                type="credito",
            )

            self.uow.accounts.save(account)

        self.uow.pse.save(tx)
        self.uow.commit()

        return {"message": "Callback procesado correctamente", "status": tx.status}
