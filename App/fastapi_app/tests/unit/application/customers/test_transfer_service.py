import pytest
from application.customers.services.transfer_service import TransferService
from tests.unit.application.customers.mock_uow import MockUnitOfWork, MockAccount

@pytest.fixture
def uow():
    uow = MockUnitOfWork()
    
    # Pre-populate test accounts
    account_out = MockAccount(id=1, customer_id=101, balance=500.0, type="ahorros")
    account_in = MockAccount(id=2, customer_id=102, balance=100.0, type="corriente")
    
    uow.accounts.add(account_out)
    uow.accounts.add(account_in)
    
    return uow

@pytest.fixture
def transfer_service(uow):
    return TransferService(uow=uow)

def test_transfer_success(transfer_service: TransferService, uow: MockUnitOfWork):
    result = transfer_service.transfer(
        from_account_id=1,
        to_account_id=2,
        amount=150.0
    )
    
    assert result["message"] == "Transferencia realizada correctamente"
    
    # Check balances were updated in the mock repository
    assert uow.accounts.get(1).balance == 350.0  # 500 - 150
    assert uow.accounts.get(2).balance == 250.0  # 100 + 150
    
    # Check transaction committed
    assert uow.committed is True
    
    # Check that movements were registered
    assert len(uow.movements.movements) == 1
    movement = uow.movements.movements[0]
    assert movement["acc_out_id"] == 1
    assert movement["acc_in_id"] == 2
    assert movement["amount"] == 150.0

def test_transfer_insufficient_funds(transfer_service: TransferService, uow: MockUnitOfWork):
    with pytest.raises(ValueError) as excinfo:
        transfer_service.transfer(
            from_account_id=1,
            to_account_id=2,
            amount=600.0 # Acc 1 only has 500
        )
    
    assert "Fondos insuficientes" in str(excinfo.value)
    
    # Balances must be untouched
    assert uow.accounts.get(1).balance == 500.0
    assert uow.accounts.get(2).balance == 100.0
    assert uow.committed is False

def test_transfer_negative_amount(transfer_service: TransferService, uow: MockUnitOfWork):
    with pytest.raises(ValueError) as excinfo:
        transfer_service.transfer(
            from_account_id=1,
            to_account_id=2,
            amount=-50.0
        )
    
    assert "El monto debe ser mayor que cero" in str(excinfo.value)
    assert uow.committed is False

def test_transfer_same_account(transfer_service: TransferService, uow: MockUnitOfWork):
    with pytest.raises(ValueError) as excinfo:
        transfer_service.transfer(
            from_account_id=1,
            to_account_id=1,
            amount=100.0
        )
    
    assert "La cuenta origen y destino no pueden ser la misma" in str(excinfo.value)
    assert uow.committed is False

def test_transfer_account_not_found(transfer_service: TransferService, uow: MockUnitOfWork):
    with pytest.raises(ValueError) as excinfo:
        transfer_service.transfer(
            from_account_id=99, # Does not exist
            to_account_id=2,
            amount=100.0
        )
    
    assert "Cuenta origen no encontrada" in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo_in:
        transfer_service.transfer(
            from_account_id=1,
            to_account_id=99, # Does not exist
            amount=100.0
        )
    
    assert "Cuenta destino no encontrada" in str(excinfo_in.value)
    assert uow.committed is False
