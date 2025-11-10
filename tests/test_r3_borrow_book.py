import pytest
from services.library_service import add_book_to_catalog, borrow_book_by_patron
from database import get_book_by_isbn

def test_borrow_book_by_patron_valid_input():
    """Test normal borrowing"""
    add_book_to_catalog("Valid Input Book", "John Author", "9043786271835", 5)
    book = get_book_by_isbn("9043786271835")
    book_id = book["id"]
    success = borrow_book_by_patron("123456", book_id)[0]
    assert success is True


def test_borrow_book_by_patron_invalid_patron_id():
    """Test with letters in patron ID"""
    add_book_to_catalog("Invalid ID Test Book", "Jane Writer", "9043786271836", 5)
    book = get_book_by_isbn("9043786271836")
    book_id = book["id"]
    success = borrow_book_by_patron("Chains", book_id)[0]
    assert success is False


def test_borrow_book_by_patron_wrong_id_length():
    """Test wrong patron ID length"""
    add_book_to_catalog("Length Validation Book", "Bob Smith", "9043786271837", 5)
    book = get_book_by_isbn("9043786271837")
    book_id = book["id"]
    success = borrow_book_by_patron("1234567", book_id)[0]
    assert success is False


def test_borrow_book_by_patron_limit():
    """Test 5-book borrowing limit"""
    add_book_to_catalog("Borrowing Limit Book", "Alice Johnson", "9043786271839", 10)
    book = get_book_by_isbn("9043786271839")
    book_id = book["id"]
    patron = "888888"
    successes = 0
    for i in range(6):
        success = borrow_book_by_patron(patron, book_id)[0]
        if success:
            successes += 1

    # Expect fewer than 6 successes if limit works.
    assert successes < 6, "Borrow limit NOT enforced: user borrowed 6 times successfully"


def test_borrow_book_unavailable():
    """Test borrowing when no copies available"""
    add_book_to_catalog("Availability Test Book", "Charlie Brown", "9043786271840", 1)
    book = get_book_by_isbn("9043786271840")
    book_id = book["id"]
    
    # First borrow should work
    success1 = borrow_book_by_patron("111111", book_id)[0]
    assert success1 is True
    
    # Second should fail
    success2 = borrow_book_by_patron("222222", book_id)[0]
    assert success2 is False

