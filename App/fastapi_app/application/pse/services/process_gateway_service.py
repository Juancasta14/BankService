from dataclasses import dataclass
from datetime import datetime
import random

@dataclass
class ProcessPSEGatewayService:
    uow: any  # SqlAlchemyPSEUnitOfWork

    def process(self, internal_order_id: str):
        tx = self.uow.pse.get_by_internal_order_id(internal_order_id)
        if tx is None:
            raise ValueError("Transacción no encontrada")

        # Expirada
        if tx.expires_at and tx.expires_at < datetime.utcnow():
            tx.status = "EXPIRED"
            tx.updated_at = datetime.utcnow()
            self.uow.commit()
            return ("failure", tx.return_url_failure)

        # Simulación PSE
        aprobado = random.random() < 0.9

        if not aprobado:
            tx.status = "REJECTED"
            tx.updated_at = datetime.utcnow()
            self.uow.commit()
            return ("failure", tx.return_url_failure)

        # Cuenta origen
        account = self.uow.accounts.get(tx.account_id)
        if account is None:
            tx.status = "REJECTED"
            tx.updated_at = datetime.utcnow()
            self.uow.commit()
            return ("failure", tx.return_url_failure)

        # Saldo suficiente
        if account.balance < tx.amount:
            tx.status = "REJECTED"
            tx.updated_at = datetime.utcnow()
            self.uow.commit()
            return ("failure", tx.return_url_failure)

        # Descontar saldo
        account.balance -= tx.amount
        tx.status = "APPROVED"
        tx.updated_at = datetime.utcnow()

        self.uow.accounts.save(account)
        self.uow.pse.save(tx)
        self.uow.commit()

        return ("success", tx.return_url_success)
