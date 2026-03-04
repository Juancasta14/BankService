import pytest
from datetime import datetime, timedelta, timezone

from application.pse.services.create_payment_service import CreatePSEPaymentService
from application.pse.services.get_payment_service import GetPSEPaymentService
from application.pse.services.process_gateway_service import ProcessPSEGatewayService
from application.pse.services.process_callback_service import ProcessPSECallbackService

from tests.unit.application.pse.mock_uow_pse import MockPSEUnitOfWork, MockAccount


@pytest.fixture
def uow():
    uow = MockPSEUnitOfWork()
    # Pongo un par de cuentas de prueba
    uow.accounts.save(MockAccount(id=1, customer_id=101, balance=5000.0))
    uow.accounts.save(MockAccount(id=2, customer_id=102, balance=20.0))

    # Pre-crear una transaccion para el callback test
    tx = uow.pse.new_tx(
        internal_order_id="PSE-12345",
        customer_id=101,
        account_id=1,
        amount=500.0,
        currency="COP",
        status="PENDING",
        provider="PSE",
        payment_url="",
        return_url_success="http://success",
        return_url_failure="http://fail",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    uow.pse.add(tx)
    return uow


# --- CREATE PAYMENT TESTS ---
def test_create_payment_success(uow):
    service = CreatePSEPaymentService(uow=uow)
    res = service.create_payment(customer_id=101, account_id=1, amount=1000.0)
    assert res["status"] == "PENDING"
    assert "PSE-" in res["internal_order_id"]
    assert uow.committed is True

    # verify it was added to repo
    saved_tx = uow.pse.get_by_internal_order_id(res["internal_order_id"])
    assert saved_tx is not None
    assert saved_tx.amount == 1000.0


def test_create_payment_insufficient_funds(uow):
    service = CreatePSEPaymentService(uow=uow)
    with pytest.raises(ValueError) as exc:
        service.create_payment(
            customer_id=101, account_id=1, amount=99999.0  # More than 5000.0
        )
    assert "Saldo insuficiente" in str(exc.value)


def test_create_payment_account_not_found(uow):
    service = CreatePSEPaymentService(uow=uow)
    with pytest.raises(ValueError) as exc:
        service.create_payment(customer_id=101, account_id=99, amount=100.0)
    assert "Cuenta de origen" in str(exc.value)


# --- GET PAYMENT TESTS ---
def test_get_payment_success(uow):
    service = GetPSEPaymentService(uow=uow)
    tx = service.get(internal_order_id="PSE-12345")
    assert tx.amount == 500.0


def test_get_payment_not_found(uow):
    service = GetPSEPaymentService(uow=uow)
    with pytest.raises(ValueError):
        service.get(internal_order_id="INVALID")


# --- PROCESS GATEWAY TESTS ---
def test_gateway_expired_transaction(uow):
    # set as expired
    tx = uow.pse.get_by_internal_order_id("PSE-12345")
    tx.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    service = ProcessPSEGatewayService(uow=uow)
    result, url = service.process("PSE-12345")

    assert result == "failure"
    assert url == "http://fail"
    assert tx.status == "EXPIRED"


def test_gateway_account_not_found_on_process(uow, monkeypatch):
    # force 100% approval
    monkeypatch.setattr("random.random", lambda: 0.1)
    tx = uow.pse.get_by_internal_order_id("PSE-12345")
    tx.account_id = 99  # invalidate account

    service = ProcessPSEGatewayService(uow=uow)
    result, url = service.process("PSE-12345")
    assert result == "failure"
    assert tx.status == "REJECTED"


def test_gateway_insufficient_funds_on_process(uow, monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.1)  # 100% approval
    tx = uow.pse.get_by_internal_order_id("PSE-12345")
    tx.amount = 99999.0  # more than acc balance

    service = ProcessPSEGatewayService(uow=uow)
    result, url = service.process("PSE-12345")
    assert result == "failure"
    assert tx.status == "REJECTED"


def test_gateway_success(uow, monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.1)  # 100% approval

    service = ProcessPSEGatewayService(uow=uow)
    result, url = service.process("PSE-12345")

    assert result == "success"
    assert url == "http://success"

    tx = uow.pse.get_by_internal_order_id("PSE-12345")
    assert tx.status == "APPROVED"
    assert uow.accounts.get(1).balance == 4500.0  # 5000 - 500


# --- PROCESS CALLBACK TESTS ---
def test_callback_success(uow):
    service = ProcessPSECallbackService(uow=uow)
    acc = uow.accounts.get(1)
    assert acc.balance == 5000.0

    res = service.process_callback(
        internal_order_id="PSE-12345",
        status="SUCCESS",
        provider_tx_id="prov-1",
        provider_reference="123",
        raw_payload={"foo": "bar"},
    )

    assert res["status"] == "SUCCESS"

    # balance should have incremented
    assert acc.balance == 5500.0

    # credit movement should be added
    assert len(uow.movements.movements) == 1
    mov = uow.movements.movements[0]
    assert mov["amount"] == 500.0
    assert "PSE-12345" in mov["description"]


def test_callback_failure_does_not_increment_balance(uow):
    service = ProcessPSECallbackService(uow=uow)
    res = service.process_callback(
        internal_order_id="PSE-12345",
        status="DECLINED",
        provider_tx_id="prov-1",
        provider_reference="123",
        raw_payload=None,
    )

    assert res["status"] == "DECLINED"
    assert uow.accounts.get(1).balance == 5000.0  # Untouched
    assert len(uow.movements.movements) == 0


def test_callback_not_found(uow):
    service = ProcessPSECallbackService(uow=uow)
    with pytest.raises(ValueError):
        service.process_callback(
            internal_order_id="INVALID",
            status="SUCCESS",
            provider_tx_id=None,
            provider_reference=None,
            raw_payload=None,
        )
