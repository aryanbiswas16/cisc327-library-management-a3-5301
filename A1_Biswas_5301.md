# Assignment 1 Status Report

Name: Aryan Biswas  
Student ID: 20295301
Group: 1 (not really sure what to put here)

## Implementation Status Table

(I REALLY TRIED TO MAKE THE TABLE WORK)

| Function (module)            | Req | Status   | What’s Missing/notes                                                                                   
|------------------------------|-----|----------|-------------------------------------------------------------------------------------------------------------|
| `add_book_to_catalog`        | R1  | Complete | Validation + duplicate ISBN check + insert OK. Could also validate all ISBN chars are digits.               |
| `borrow_book_by_patron`      | R3  | Partial  | Borrow limit logic uses `> 5` so a 6th borrow is allowed (should be `>= 5`).                                |
| `return_book_by_patron`      | R4  | Missing  | Needs active borrow check, return date update, availability increment, late fee integration.                |
| `calculate_late_fee_for_book`| R5  | Missing  | Implement 14‑day due logic and tiered fees (0.50 first 7 days, 1.00 after) and $15 cap also JSON-style return.     |
| `search_books_in_catalog`    | R6  | Missing  | Case-insensitive partial title/author match, exact ISBN match, return list of book dicts.                   |
| `get_patron_status_report`   | R7  | Missing  | Aggregate current borrows (with due, overdue calc, fees), history, counts, total fees. UI link not present. |

Requirement testing summary:

**Function Name: add_book_to_catalog** 

Summary:

test_add_book_valid_input : Checks if you can add a book normally with good data.

test_add_book_invalid_isbn_too_short : Makes sure the function rejects short ISBNs (like 9 digits instead of 13).

test_add_book_missing_title : Tries adding a book with no title - should fail.

test_add_book_title_too_long : Tests what happens when the title is way too long (over 200 chars).

test_add_book_zero_copies : Checks that you can't add a book with 0 copies.

**Function Name: borrow_book_by_patron** 

Summary:

test_borrow_book_by_patron_valid_input : Tests normal borrowing - should work fine.

test_borrow_book_by_patron_invalid_patron_id : Tries to borrow with letters in the patron ID (like "Chains").

test_borrow_book_by_patron_wrong_id_length : Uses wrong length patron ID (7 digits instead of 6).

test_borrow_book_by_patron_limit : Tries to borrow 6 books with the same person to test the 5-book limit.

test_borrow_book_unavailable : Attempts to borrow when there are no copies left.

**Function Name: return_book_by_patron** 

Summary:

test_return_book_by_patron_valid_input : Tests returning a book normally after borrowing it.

test_return_book_not_borrowed_by_patron : Tries to return a book that someone else borrowed - should fail.

test_return_book_twice : Attempts to return the same book twice (double return).

test_return_book_invalid_book_id : Tries returning with a fake book ID that doesn't exist.

**Function Name: calculate_late_fee_for_book** 

Summary:

test_fee_not_overdue : Checks that books returned on time have no fee.

test_fee_overdue_manual_record : Tests fee calculation for a book that's 10 days late (should be $6.50).

test_fee_cap_cannot_exceed_15 : Makes sure fees don't go over $15 even for really late books.

test_fee_one_day_overdue : Tests the minimum fee for just 1 day late (should be $0.50).

**Function Name: search_books_in_catalog**

Summary:

test_search_books_in_catalog_valid_input : Searches for a book by exact title.

test_search_books_in_catalog_isbn_exact_match : Searches using the full ISBN number.

test_search_books_in_catalog_title_case_insensitive : Tests if search works with different capitalization.

test_search_books_by_author : Searches for books by author name.

**Function Name: get_patron_status_report** 

Summary:

test_nonexistent_patron : Tries to get status for a patron that doesn't exist.

test_patron_id_with_letters : Uses an invalid patron ID with letters in it.

test_status_placeholder_empty_or_invalid_length : Tests different wrong patron ID lengths (too short, too long, empty).

test_status_placeholder_repeat_call_consistent : Calls the function twice to make sure it gives the same result.

test_get_patron_status_report_valid_input : Tests getting a proper status report for a real patron who borrowed books.




How I used AI in this assignment:

I used it to help me understand and learn pytest and how it works,I also used it to help me format my md file properly because I was having trouble. And I also used it to help me debug the code. 