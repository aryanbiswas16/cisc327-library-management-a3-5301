import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

# ---------------- pay_late_fees() tests ----------------

def test_pay_late_fees_successful_payment(mocker):
    """Test successful payment"""
    # Stub database functions with fake data
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={'fee_amount': 10.50, 'days_overdue': 15, 'status': 'success'})
    
    mocker.patch('services.library_service.get_book_by_id',
                 return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
    
    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123456", "Payment successful")
    
    success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is True
    assert transaction_id == "txn_123456"
    mock_gateway.process_payment.assert_called_once()
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=10.50,
        description="Late fees for 'Test Book'"
    )



def test_pay_late_fees_payment_declined(mocker):
    """Test payment declined by gateway"""
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={'fee_amount': 5.00, 'days_overdue': 5, 'status': 'success'})
    
    mocker.patch('services.library_service.get_book_by_id',
                 return_value={'id': 2, 'title': 'Another Book', 'author': 'Another Author'})
    
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Insufficient funds")
    
    success, message, transaction_id = pay_late_fees("654321", 2, mock_gateway)
    
    assert success is False
    assert "Payment failed" in message
    assert transaction_id is None


def test_pay_late_fees_invalid_patron_id():
    """Test with invalid patron ID"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, transaction_id = pay_late_fees("12345", 1, mock_gateway)
    
    assert success is False
    assert transaction_id is None
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_late_fees(mocker):
    """Test when there are no late fees"""
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={'fee_amount': 0.00, 'days_overdue': 0, 'status': 'success'})
    
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is False
    assert transaction_id is None
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_book_not_found(mocker):
    """Test when book doesn't exist"""
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={'fee_amount': 5.00, 'days_overdue': 5, 'status': 'success'})
    mocker.patch('services.library_service.get_book_by_id', return_value=None)
    
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message, transaction_id = pay_late_fees("123456", 999, mock_gateway)
    
    assert success is False
    assert "Book not found" in message
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker):
    """Test network error exception handling"""
    mocker.patch('services.library_service.calculate_late_fee_for_book',
                 return_value={'fee_amount': 7.50, 'days_overdue': 10, 'status': 'success'})
    mocker.patch('services.library_service.get_book_by_id',
                 return_value={'id': 3, 'title': 'Test Book', 'author': 'Test Author'})
    
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = ConnectionError("Network timeout")
    
    success, message, transaction_id = pay_late_fees("123456", 3, mock_gateway)
    
    assert success is False
    assert "error" in message.lower()
    assert transaction_id is None



# ---------------- refund_late_fee_payment() tests ----------------

def test_refund_late_fee_payment_successful():
    """Test successful refund"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund processed successfully")
    
    success, message = refund_late_fee_payment("txn_123456", 10.50, mock_gateway)
    
    assert success is True
    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_once_with("txn_123456", 10.50)


def test_refund_invalid_transaction_id_empty():
    """Test refund with empty transaction ID"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("", 5.00, mock_gateway)
    
    assert success is False
    mock_gateway.refund_payment.assert_not_called()


def test_refund_invalid_transaction_id_format():
    """Test transaction ID without txn_ prefix"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("invalid_123", 5.00, mock_gateway)
    
    assert success is False
    mock_gateway.refund_payment.assert_not_called()


def test_refund_negative_amount():
    """Test refund with negative amount"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("txn_123456", -5.00, mock_gateway)
    
    assert success is False
    mock_gateway.refund_payment.assert_not_called()


def test_refund_zero_amount():
    """Test refund with zero amount"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("txn_123456", 0.00, mock_gateway)
    
    assert success is False
    mock_gateway.refund_payment.assert_not_called()


def test_refund_exceeds_maximum():
    """Test refund amount over $15"""
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("txn_123456", 20.00, mock_gateway)
    
    assert success is False
    mock_gateway.refund_payment.assert_not_called()


def test_refund_exactly_maximum():
    """Test refund with exactly $15.00"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $15.00 processed")
    
    success, message = refund_late_fee_payment("txn_123456", 15.00, mock_gateway)
    
    assert success is True
    mock_gateway.refund_payment.assert_called_once()


def test_refund_gateway_fails():
    """Test when gateway returns failure"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Transaction already refunded")
    
    success, message = refund_late_fee_payment("txn_123456", 10.00, mock_gateway)
    
    assert success is False
    assert "Refund failed" in message


def test_refund_exception_handling():
    """Test exception from gateway"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.side_effect = TimeoutError("Connection timeout")
    
    success, message = refund_late_fee_payment("txn_123456", 8.00, mock_gateway)
    
    assert success is False
    assert "error" in message.lower()


# ---------------- PaymentGateway tests ----------------

def test_gateway_creates_successfully():
    """Test creating a payment gateway"""
    gateway = PaymentGateway()
    assert gateway.api_key == "test_key_12345"


def test_gateway_with_custom_key():
    """Test gateway with different key"""
    gateway = PaymentGateway(api_key="custom_key_999")
    assert gateway.api_key == "custom_key_999"


def test_process_payment_works():
    """Test that payment goes through"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("123456", 10.50, "Late fees")
    
    assert success is True
    assert "txn_123456" in txn_id


def test_process_payment_zero_amount():
    """Test payment with $0"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("123456", 0, "Test")
    
    assert success is False


def test_process_payment_negative_amount():
    """Test payment with negative money"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("123456", -5.00, "Test")
    
    assert success is False


def test_process_payment_too_much():
    """Test payment over limit"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("123456", 1500.00, "Big payment")
    
    assert success is False


def test_process_payment_bad_patron_id():
    """Test payment with wrong patron ID"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("12345", 10.00, "Test")
    
    assert success is False


def test_process_payment_patron_id_too_long():
    """Test patron ID with too many digits"""
    gateway = PaymentGateway()
    success, txn_id, message = gateway.process_payment("1234567", 10.00, "Test")
    
    assert success is False


def test_refund_works():
    """Test refund goes through"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456_1234567890", 10.50)
    
    assert success is True


def test_refund_bad_transaction_id():
    """Test refund with wrong ID"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("invalid_id", 10.00)
    
    assert success is False


def test_refund_empty_transaction_id():
    """Test refund with no ID"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("", 10.00)
    
    assert success is False


def test_refund_zero_dollars():
    """Test refund $0"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456", 0)
    
    assert success is False


def test_refund_negative_dollars():
    """Test refund negative amount"""
    gateway = PaymentGateway()
    success, message = gateway.refund_payment("txn_123456", -5.00)
    
    assert success is False


def test_verify_status_works():
    """Test checking payment status"""
    gateway = PaymentGateway()
    status = gateway.verify_payment_status("txn_123456_1234567890")
    
    assert status["status"] == "completed"


def test_verify_status_bad_id():
    """Test status check with bad ID"""
    gateway = PaymentGateway()
    status = gateway.verify_payment_status("invalid_id")
    
    assert status["status"] == "not_found"


def test_verify_status_empty_id():
    """Test status check with empty ID"""
    gateway = PaymentGateway()
    status = gateway.verify_payment_status("")
    
    assert status["status"] == "not_found"
