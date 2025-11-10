import pytest
from services.library_service import add_book_to_catalog, search_books_in_catalog


def test_search_books_in_catalog_valid_input():
    """Should return at least one matching book by exact title."""
    add_book_to_catalog("Test Book", "Test Author", "9014567890123", 5)
    result = search_books_in_catalog("Test Book", "title")
    assert isinstance(result, list)
    assert len(result) >= 1
    assert result[0]["title"] == "Test Book"



def test_search_books_in_catalog_isbn_exact_match():
    """Exact ISBN search should return the specific matching book."""
    add_book_to_catalog("ISBN Match Book", "Some Author", "9014567890992", 4)
    result = search_books_in_catalog("9014567890992", "isbn")
    assert isinstance(result, list)
    assert result[0]["isbn"] == "9014567890992"


def test_search_books_in_catalog_title_case_insensitive():
    """Test case-insensitive partial title matching."""
    add_book_to_catalog("Deep Learning With Python", "Some Author", "9014567890991", 2)

    res1 = search_books_in_catalog("Deep Learning", "title")
    res2 = search_books_in_catalog("deep learning", "title")

    assert isinstance(res1, list)
    assert isinstance(res2, list)
    assert len(res1) > 0
    assert len(res2) > 0

    # Just compare first titles lowercased
    assert res1[0]["title"].lower().startswith("deep learning")
    assert res2[0]["title"].lower().startswith("deep learning")


def test_search_books_by_author():
    """Simple test for author search functionality."""
    add_book_to_catalog("Simple Book", "Jane Smith", "9014567890888", 3)
    result = search_books_in_catalog("Jane Smith", "author")
    assert isinstance(result, list)
    assert result[0]["author"] == "Jane Smith"


