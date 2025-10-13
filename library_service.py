"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_db_connection, get_book_by_id, get_book_by_isbn, 
    get_patron_borrow_count, insert_book, insert_borrow_record, 
    update_book_availability, update_borrow_record_return_date, 
    get_all_books, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if not isbn.isdigit() or len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        book_title = title.strip()
        return True, 'Book "' + book_title + '" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    book_title = book["title"]
    
    year = str(due_date.year)
    month = str(due_date.month)
    day = str(due_date.day)
    due_date_string = year + '-' + month + '-' + day
    
    return True, 'Successfully borrowed "' + book_title + '". Due date: ' + due_date_string + '.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4 as per requirements
    
    Steps:
    1. Check if patron ID is valid
    2. Check if book exists
    3. Check if this patron actually borrowed this book
    4. Record the return date
    5. Add the book back to available copies
    """
    if len(patron_id) != 6 or not patron_id.isdigit():
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    book_is_borrowed = False
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
            book_is_borrowed = True
            break
    
    if not book_is_borrowed:
        return False, "This book was not borrowed by you or has already been returned."
    
    # Calculate late fees BEFORE processing the return
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    today = datetime.now()
    success = update_borrow_record_return_date(patron_id, book_id, today)
    if not success:
        return False, "Database error occurred while recording return."
    
    success = update_book_availability(book_id, 1)
    if not success:
        return False, "Database error occurred while updating book availability."
    
    # Build success message with book title
    message = 'Successfully returned "' + book["title"] + '".'
    
    # Add late fee if there is one
    if fee_info['fee_amount'] > 0:
        # Round to 2 decimal places for money display
        fee_amount = round(fee_info['fee_amount'], 2)
        message = message + ' Amount due: $' + str(fee_amount) + '.'
    
    return True, message

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5 as per requirements
    
    Fee rules:
    - First 7 days overdue: $0.50 per day
    - After 7 days: $1.00 per day
    - Maximum fee: $15.00 per book
    """
    if len(patron_id) != 6 or not patron_id.isdigit():
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid patron ID'}
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    due_date = None
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
            due_date = borrowed_book['due_date']
            break
    
    if not due_date:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No active borrow record found'}
    today = datetime.now()
    days_overdue = (today - due_date).days
    
    if days_overdue <= 0:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'success'}
    
    fee = 0.00
    
    if days_overdue <= 7:
        fee = days_overdue * 0.50
    else:
        fee = 7 * 0.50  # First 7 days
        fee = fee + (days_overdue - 7) * 1.00  # Remaining days
    
    if fee > 15.00:
        fee = 15.00
    
    return {'fee_amount': fee, 'days_overdue': days_overdue, 'status': 'success'}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6 as per requirements
    
    Search types:
    - 'title': finds books with matching title (partial match)
    - 'author': finds books with matching author (partial match) 
    - 'isbn': finds book with exact ISBN match
    """
    if not search_term:
        return []
    
    search_term = search_term.strip()
    if not search_term:
        return []
    
    if search_type == 'isbn':
        book = get_book_by_isbn(search_term)
        if book:
            return [book]
        else:
            return []
    
    elif search_type == 'title':
        all_books = get_all_books()
        results = []
        for book in all_books:
            if search_term.lower() in book['title'].lower():
                results.append(book)
        return results
    
    elif search_type == 'author':
        all_books = get_all_books()
        results = []
        for book in all_books:
            if search_term.lower() in book['author'].lower():
                results.append(book)
        return results
    
    else:
        return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7 as per requirements
    
    Returns information about what books they have borrowed,
    any late fees, and their borrowing history.
    """
    if len(patron_id) != 6 or not patron_id.isdigit():
        return {}
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    total_fees = 0.00
    for book in borrowed_books:
        book_id = book['book_id']
        fee_info = calculate_late_fee_for_book(patron_id, book_id)
        fee_amount = fee_info['fee_amount']
        total_fees = total_fees + fee_amount
    
    conn = get_db_connection()
    borrow_records = conn.execute('''
        SELECT book_id, borrow_date, due_date, return_date
        FROM borrow_records
        WHERE patron_id = ?
    ''', (patron_id,)).fetchall()
    conn.close()
    
    history = []
    for record in borrow_records:
        book_id = record['book_id']
        book = get_book_by_id(book_id)
        
        if record['return_date']:
            status = 'Returned'
        else:
            status = 'Currently Borrowed'
        
        record_info = {
            'book_id': book_id,
            'title': book['title'],
            'author': book['author'],
            'borrow_date': record['borrow_date'],
            'due_date': record['due_date'],
            'return_date': record['return_date'],
            'status': status
        }
        history.append(record_info)
    
    number_of_books_borrowed = len(borrowed_books)
    
    report = {
        'patron_id': patron_id,
        'Currently Borrowed': number_of_books_borrowed,
        'borrowed_books': borrowed_books,
        'total_late_fees': total_fees,
        'borrowing_history': history
    }
    
    return report