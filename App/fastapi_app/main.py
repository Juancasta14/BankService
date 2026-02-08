from fastapi import FastAPI
from models import Base
from fastapi_app.adapters.inbound.http.routes.auth_routes import router as auth_router
from fastapi_app.adapters.inbound.http.routes.transfers import router as transfer_router
from fastapi_app.adapters.inbound.http.routes.pse_payments import router as pse_payments_router
from fastapi_app.adapters.inbound.http.routes.pse_gateway import router as pse_gateway_router
from fastapi_app.adapters.inbound.http.routes.pse_callback import router as pse_callback_router
from fastapi_app.adapters.inbound.http.routes.payments_query import router as payments_query_router
from fastapi_app.adapters.inbound.http.routes.customers import router as customers_router



from fastapi_app.adapters.inbound.http.dependencies import get_current_user
from fastapi_app.adapters.outbound.persistence.sqlalchemy.models import UserDB



app = FastAPI(title="Bank Service with Auth")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(transfer_router)
app.include_router(pse_payments_router)
app.include_router(pse_gateway_router)
app.include_router(pse_callback_router)
app.include_router(payments_query_router)
app.include_router(customers_router)



