from dataclasses import dataclass
from datetime import datetime

@dataclass
class TransferService:
    uow: any  # UnitOfWork

    def transfer(self, *, from_account_id: int, to_account_id: int, amount: float):
        if amount <= 0:
            raise ValueError("El monto debe ser mayor que cero")

        if from_account_id == to_account_id:
            raise ValueError("La cuenta origen y destino no pueden ser la misma")

        acc_out = self.uow.accounts.get(from_account_id)
        if not acc_out:
            raise ValueError("Cuenta origen no encontrada")

        acc_in = self.uow.accounts.get(to_account_id)
        if not acc_in:
            raise ValueError("Cuenta destino no encontrada")

        if acc_out.balance < amount:
            raise ValueError("Fondos insuficientes")

        # Actualizar balances
        acc_out.balance -= amount
        acc_in.balance += amount

        # Movimientos
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        self.uow.movements.add_transfer_movements(
            acc_out_id=acc_out.id,
            acc_in_id=acc_in.id,
            customer_out_id=acc_out.customer_id,
            customer_in_id=acc_in.customer_id,
            acc_out_type=getattr(acc_out, "type", None),
            acc_in_type=getattr(acc_in, "type", None),
            date=date_str,
            amount=amount,
        )

        self.uow.accounts.save(acc_out)
        self.uow.accounts.save(acc_in)

        self.uow.commit()

        return {"message": "Transferencia realizada correctamente"}
