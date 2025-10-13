import pytest
from library_service import return_book_by_patron, calculate_late_fee_for_book, add_book_to_catalog, borrow_book_by_patron
from database import get_book_by_isbn, insert_book, insert_borrow_record
from datetime import datetime, timedelta
# ---------------- R4: return_book_by_patron ----------------

def test_return_book_by_patron_valid_input():
    """Test Proper Input"""
    add_book_to_catalog("Test Book", "Test Author", "9043786271835", 5)
    book = get_book_by_isbn("9043786271835")
    book_id = book["id"]
    borrow_book_by_patron("123456", book_id)
    success, message = return_book_by_patron("123456", book_id)
    assert success is True


def test_return_book_not_borrowed_by_patron():
    """Test returning book borrowed by someone else"""
    add_book_to_catalog("Shared Test Book", "Auth Z", "9994567890124", 1)
    book = get_book_by_isbn("9994567890124")
    book_id = book["id"]
    borrow_book_by_patron("111111", book_id)
    success, message = return_book_by_patron("222222", book_id)
    assert success is False


def test_return_book_twice():
    """Test returning the same book twice"""
    add_book_to_catalog("Twice Return Book", "Author T", "9043786271836", 1)
    book = get_book_by_isbn("9043786271836")
    book_id = book["id"]
    borrow_book_by_patron("123456", book_id)
    success1, message1 = return_book_by_patron("123456", book_id)
    assert success1 is True
    success2, message2 = return_book_by_patron("123456", book_id)
    assert success2 is False


def test_return_book_invalid_book_id():
    """Test returning with invalid book ID"""
    success, message = return_book_by_patron("123456", 99999999)
    assert success is False
    
 

# ---------------- R5: calculate_late_fee_for_book ----------------

"""
tests for late fee calculation 
"""

def test_fee_not_overdue():
    """Test fee for book returned on time"""
    add_book_to_catalog("No Overdue Book", "Author N", "9014567890990", 3)
    book = get_book_by_isbn("9014567890990")
    book_id = book["id"]
    borrow_book_by_patron("123456", book_id)
    res = calculate_late_fee_for_book("123456", book_id)
    assert res["days_overdue"] == 0
    assert res["fee_amount"] == 0.00


def test_fee_overdue_manual_record():
    """Test fee calculation for overdue book"""
    insert_book("Overdue Case Book", "Author O", "9014567890999", 1, 1)
    book = get_book_by_isbn("9014567890999")
    book_id = book["id"]
    now = datetime.now()
    insert_borrow_record("123456", book_id, now - timedelta(days=24), now - timedelta(days=10))
    res = calculate_late_fee_for_book("123456", book_id)
    assert res["days_overdue"] == 10
    assert res["fee_amount"] == 6.50


def test_fee_cap_cannot_exceed_15():
    """Test fee cap at $15"""
    insert_book("Super Overdue Book", "Author P", "9014567890998", 1, 1)
    book = get_book_by_isbn("9014567890998")
    book_id = book["id"]
    now = datetime.now()
    insert_borrow_record("123456", book_id, now - timedelta(days=54), now - timedelta(days=40))
    res = calculate_late_fee_for_book("123456", book_id)
    assert res["fee_amount"] == 15.00


def test_fee_one_day_overdue():
    """Minimal overdue case: 1 day overdue should cost $0.50 (first 7 days rate)"""
    insert_book("One Day Overdue", "Author Q", "9014567890997", 1, 1)
    book = get_book_by_isbn("9014567890997")
    book_id = book["id"]
    now = datetime.now()
    insert_borrow_record("123456", book_id, now - timedelta(days=15), now - timedelta(days=1))
    res = calculate_late_fee_for_book("123456", book_id)
    assert res["days_overdue"] == 1
    assert res["fee_amount"] == 0.50



    
    




