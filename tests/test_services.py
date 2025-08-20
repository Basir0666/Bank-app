
import os
import pytest
from src.services import AccountService

# NOTE: For a real test, you'd point to a test database or use transactions and rollbacks.
# These are illustrative and may require a pre-seeded DB to pass consistently.

def test_deposit_and_withdraw():
    svc = AccountService()
    acc_no = svc.create_user_and_account("Test User", "test@example.com", "1234")
    bal = svc.deposit(acc_no, 100.0, note="test deposit")
    assert bal >= 100.0
    bal2 = svc.withdraw(acc_no, 40.0, note="test withdraw")
    assert round(bal2,2) == round(bal-40.0,2)

def test_lock_on_wrong_pin():
    svc = AccountService()
    acc_no = svc.create_user_and_account("Lock User", "lock@example.com", "4321")
    for i in range(2):
        with pytest.raises(Exception):
            svc.authenticate(acc_no, "0000")
    # third attempt should lock
    with pytest.raises(Exception):
        svc.authenticate(acc_no, "0000")
    # now even correct PIN should show locked
    with pytest.raises(Exception):
        svc.authenticate(acc_no, "4321")
