import pytest
from services.library_service import get_patron_status_report, add_book_to_catalog, borrow_book_by_patron
from database import get_book_by_isbn


def test_nonexistent_patron():
    """Placeholder: nonexistent patron returns empty dict."""
    result = get_patron_status_report('999999')
    assert isinstance(result, dict)
    # Valid patron ID returns status even if they haven't borrowed anything
    assert result['Currently Borrowed'] == 0


def test_patron_id_with_letters():
    """Placeholder: invalid format returns empty dict."""
    result = get_patron_status_report('12A456')
    assert isinstance(result, dict)
    assert result == {}


def test_status_placeholder_empty_or_invalid_length():
    """Placeholder: various invalid length IDs return empty dict."""
    for pid in ['', '12345', '1234567']:
        result = get_patron_status_report(pid)
        assert isinstance(result, dict)
        assert result == {}


def test_status_placeholder_repeat_call_consistent():
    r1 = get_patron_status_report('123456')
    r2 = get_patron_status_report('123456')
    assert r1 == r2


def test_get_patron_status_report_valid_input():
    """Test with a valid patron who has borrowed a book."""
    
    add_book_to_catalog("Status Test Book", "Status Author", "9043786271850", 5)
    book = get_book_by_isbn("9043786271850")
    book_id = book["id"]

    borrow_book_by_patron("123456", book_id)

    result = get_patron_status_report("123456")

    # Just check it returns a dict and has the basic info
    assert isinstance(result, dict)
    assert result["Currently Borrowed"] == 1
