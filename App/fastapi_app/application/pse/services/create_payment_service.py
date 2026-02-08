from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

@dataclass
class CreatePSEPaymentService:
    uow: any  # UnitOfWork (si quieres tipado fuerte, lo ponemos)

    def create_payment(
        self,
        *,
        customer_id: int,
        account_id: int,
        amount: float,
        currency: str = "COP",
        return_url_success: str | None = None,
        return_url_failure: str | None = None,
    ) -> dict:
        # 1) cuenta existe
        account = self.uow.accounts.get(account_id)
        if account is None:
            raise ValueError("Cuenta de origen no encontrada")

        # 2) saldo suficiente (tu comportamiento actual)
        if account.balance < amount:
            raise ValueError(f"Saldo insuficiente en la cuenta #{account.id}. Saldo disponible: {account.balance:.2f}")

        # 3) crear tx
        internal_order_id = f"PSE-{uuid4().hex[:20]}"

        # tx = PSETransactionDB(...)  <-- lo crea el adaptador (o lo creas aquí si importas el modelo)
        tx = self.uow.pse.new_tx(  # si prefieres, creamos un método factory en repo
            internal_order_id=internal_order_id,
            customer_id=customer_id,
            account_id=account_id,
            amount=amount,
            currency=currency,
            status="PENDING",
            provider="PSE",
            payment_url="",
            return_url_success=return_url_success,
            return_url_failure=return_url_failure,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )

        self.uow.pse.add(tx)
        self.uow.commit()

        return {
            "id": tx.id,
            "internal_order_id": tx.internal_order_id,
            "status": tx.status,
        }
