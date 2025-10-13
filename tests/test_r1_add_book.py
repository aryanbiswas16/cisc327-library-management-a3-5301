import pytest
from library_service import add_book_to_catalog


def test_add_book_valid_input():
    """Test adding a book with valid input."""
    
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    assert success is True
    assert "successfully added" in message.lower()


def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    assert success is False
    assert "13 digits" in message


def test_add_book_missing_title():
    """Missing title should fail."""
    
    success, message = add_book_to_catalog("", "Author", "9876543210123", 1)
    assert success is False
    assert "title is required" in message.lower()


def test_add_book_title_too_long():
    """Title longer than 200 chars should fail."""
    
    long_title = "x" * 201
    success, message = add_book_to_catalog(long_title, "Author", "9876543210124", 1)
    assert success is False
    assert "less than 200" in message.lower()


def test_add_book_zero_copies():
    """Zero total copies invalid."""
    
    success, message = add_book_to_catalog("Another", "Author", "9876543210125", 0)
    assert success is False
    assert "positive integer" in message.lower()
