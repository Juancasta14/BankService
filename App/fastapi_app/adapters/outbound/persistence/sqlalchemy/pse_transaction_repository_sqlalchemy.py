import json
from sqlalchemy.orm import Session
from fastapi_app.adapters.outbound.persistence.sqlalchemy.models import PSETransactionDB



class PSETransactionRepositorySqlAlchemy:
    def __init__(self, db: Session):
        self.db = db

    def new_tx(self, **kwargs):
        return PSETransactionDB(**kwargs)

    def get_by_internal_order_id(self, internal_order_id: str):
        return (
            self.db.query(PSETransactionDB)
            .filter(PSETransactionDB.internal_order_id == internal_order_id)
            .first()
        )

    def add(self, tx) -> None:
        self.db.add(tx)

    def save(self, tx) -> None:
        self.db.add(tx)

    def serialize_payload(self, raw_payload: dict | None) -> str:
        # Evita errores si viene None y mantiene caracteres (tildes, ñ)
        return json.dumps(raw_payload or {}, ensure_ascii=False)
