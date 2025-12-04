from playwright.sync_api import Page, expect

def test_e2e_add_and_borrow(page: Page, base_url: str):
    """
    Flow:
    Add a book
    Open catalog and find the book
    Borrow the book from that row
    Check for confirmation
    """

    page.goto(base_url + "/add_book")
    page.fill('input[name="title"]', "E2E Book")
    page.fill('input[name="author"]', "Student Author")
    page.fill('input[name="isbn"]', "9999999999999")
    page.fill('input[name="total_copies"]', "1")
    page.get_by_role("button", name="Add Book to Catalog").click()

    page.goto(base_url + "/catalog")

    row = page.locator("table tbody tr").filter(has_text="E2E Book").first
    row.wait_for(state="visible", timeout=5000)
    text = row.inner_text().lower()
    assert "student author" in text
    assert "9999999999999" in text

    patron_input = row.locator('input[name="patron_id"]')
    patron_input.fill("123456")
    row.get_by_role("button", name="Borrow").click()

    body_text = page.locator("body").inner_text()
    assert "borrow" in body_text.lower() or "successfully" in body_text.lower()