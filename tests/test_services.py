import pytest
from app.services.auth import AuthService, pwd_context
from app.services.payment import PaymentService
from app.schemas.payment import WebhookRequest
from decimal import Decimal


def test_password_hash_and_verify():
    password = "testpassword123"
    hashed = pwd_context.hash(password)
    assert pwd_context.verify(password, hashed)
    assert not pwd_context.verify("wrongpassword", hashed)


def test_verify_signature_valid():
    from tests.conftest import make_signature, SECRET_KEY

    sig = make_signature(
        account_id=1,
        amount=100,
        transaction_id="test-txn",
        user_id=1,
        secret_key=SECRET_KEY,
    )
    assert len(sig) == 64


def test_verify_signature_invalid():
    from app.services.payment import PaymentService

    data = WebhookRequest(
        transaction_id="test-txn",
        account_id=1,
        user_id=1,
        amount=100,
        signature="invalid",
    )
    service = PaymentService(session=None)
    assert service.verify_signature(data) is False


def test_signature_is_deterministic():
    from tests.conftest import make_signature

    sig1 = make_signature(account_id=1, amount=100, transaction_id="txn1", user_id=1)
    sig2 = make_signature(account_id=1, amount=100, transaction_id="txn1", user_id=1)
    assert sig1 == sig2


def test_signature_changes_with_different_amount():
    from tests.conftest import make_signature

    sig1 = make_signature(account_id=1, amount=100, transaction_id="txn1", user_id=1)
    sig2 = make_signature(account_id=1, amount=200, transaction_id="txn1", user_id=1)
    assert sig1 != sig2


def test_signature_changes_with_different_transaction_id():
    from tests.conftest import make_signature

    sig1 = make_signature(account_id=1, amount=100, transaction_id="txn1", user_id=1)
    sig2 = make_signature(account_id=1, amount=100, transaction_id="txn2", user_id=1)
    assert sig1 != sig2


def test_signature_changes_with_different_user_id():
    from tests.conftest import make_signature

    sig1 = make_signature(account_id=1, amount=100, transaction_id="txn1", user_id=1)
    sig2 = make_signature(account_id=1, amount=100, transaction_id="txn1", user_id=2)
    assert sig1 != sig2


def test_signature_changes_with_different_account_id():
    from tests.conftest import make_signature

    sig1 = make_signature(account_id=1, amount=100, transaction_id="txn1", user_id=1)
    sig2 = make_signature(account_id=2, amount=100, transaction_id="txn1", user_id=1)
    assert sig1 != sig2


def test_signature_concatenation_order():
    from tests.conftest import SECRET_KEY
    import hashlib

    concat = "1100test-txn1" + SECRET_KEY
    expected = hashlib.sha256(concat.encode()).hexdigest()
    from tests.conftest import make_signature

    actual = make_signature(
        account_id=1,
        amount=100,
        transaction_id="test-txn",
        user_id=1,
        secret_key=SECRET_KEY,
    )
    assert actual == expected
