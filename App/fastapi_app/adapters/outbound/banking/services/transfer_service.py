from dataclasses import dataclass
from datetime import datetime

from bankservice.domain.banking.exceptions import (
    InvalidAmount, SameAccount, AccountNotFound, InsufficientFunds
)
from bankservice.application.banking.ports.outbound.unit_of_work import UnitOfWork

@dataclass
class TransferService:
    uow: UnitOfWork

    def transfer(self, from_account_id: int, to_account_id: int, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmount("El monto debe ser mayor que cero")
        if from_account_id == to_account_id:
            raise SameAccount("La cuenta origen y destino no pueden ser iguales")

        acc_out = self.uow.accounts.get(from_account_id)
        acc_in  = self.uow.accounts.get(to_account_id)

        if not acc_out:
            raise AccountNotFound("Cuenta de origen no encontrada")
        if not acc_in:
            raise AccountNotFound("Cuenta de destino no encontrada")

        if acc_out.balance < amount:
            raise InsufficientFunds("Fondos insuficientes en la cuenta de origen")

        # negocio
        acc_out.balance -= amount
        acc_in.balance  += amount

        date_str = datetime.now().strftime("%Y-%m-%d")

        # persistencia (por puertos)
        self.uow.accounts.save(acc_out)
        self.uow.accounts.save(acc_in)

        self.uow.movements.add_transfer_movements(
            acc_out_id=acc_out.id,
            acc_in_id=acc_in.id,
            customer_out_id=acc_out.customer_id,
            customer_in_id=acc_in.customer_id,
            acc_out_type=acc_out.type,
            acc_in_type=acc_in.type,
            amount=amount,
            date_str=date_str,
        )

        self.uow.commit()
