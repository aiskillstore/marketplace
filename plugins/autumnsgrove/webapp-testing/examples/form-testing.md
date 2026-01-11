# Form Testing Examples

## Contact Form Testing

```python
from playwright.sync_api import Page, expect
import pytest

def test_contact_form_submission(page: Page):
    """Test complete contact form submission flow."""
    page.goto("https://example.com/contact")

    # Fill multi-field form
    page.fill("#name", "John Doe")
    page.fill("#email", "john@example.com")
    page.fill("#phone", "+1-555-0123")
    page.select_option("#country", "United States")
    page.check("#newsletter")
    page.fill("#message", "This is a test message for the contact form.")

    # Handle file upload
    page.set_input_files("#attachment", "path/to/test-file.pdf")

    # Submit form
    page.click("button[type='submit']")

    # Verify success message
    expect(page.locator(".success-message")).to_be_visible()
    expect(page.locator(".success-message")).to_contain_text("Thank you for contacting us")

def test_form_validation_messages(page: Page):
    """Test client-side validation messages."""
    page.goto("https://example.com/contact")

    # Try to submit with invalid email
    page.fill("#email", "invalid-email")
    page.fill("#name", "John")
    page.click("button[type='submit']")

    # Check validation message
    email_error = page.locator("#email-error")
    expect(email_error).to_be_visible()
    expect(email_error).to_contain_text("valid email")

def test_dropdown_selections(page: Page):
    """Test dropdown menu selections."""
    page.goto("https://example.com/form")

    # Select by value
    page.select_option("#category", value="electronics")

    # Select by label
    page.select_option("#country", label="Canada")

    # Select by index
    page.select_option("#priority", index=2)

    # Verify selections
    expect(page.locator("#category")).to_have_value("electronics")
```

## File Upload and Download Testing

```python
from playwright.sync_api import Page, expect
import os

def test_file_upload(page: Page):
    """Test file upload functionality."""
    page.goto("https://example.com/upload")

    # Upload single file
    page.set_input_files("#file-input", "path/to/test-document.pdf")

    # Verify file name appears
    expect(page.locator(".uploaded-file-name")).to_contain_text("test-document.pdf")

    # Submit upload
    page.click("button:text('Upload')")

    # Verify success
    expect(page.locator(".upload-success")).to_be_visible()

def test_multiple_file_upload(page: Page):
    """Test uploading multiple files."""
    page.goto("https://example.com/upload")

    # Upload multiple files
    page.set_input_files("#file-input", [
        "path/to/file1.jpg",
        "path/to/file2.jpg",
        "path/to/file3.jpg"
    ])

    # Verify all files listed
    file_list = page.locator(".file-list-item")
    expect(file_list).to_have_count(3)

def test_file_download(page: Page):
    """Test file download functionality."""
    page.goto("https://example.com/downloads")

    # Start waiting for download before clicking
    with page.expect_download() as download_info:
        page.click("a:text('Download Report')")

    download = download_info.value

    # Verify download
    assert download.suggested_filename == "report.pdf"

    # Save to specific path
    download.save_as("downloads/report.pdf")

    # Verify file was saved
    assert os.path.exists("downloads/report.pdf")

def test_drag_drop_file_upload(page: Page):
    """Test drag-and-drop file upload."""
    page.goto("https://example.com/upload")

    # Read file as buffer
    with open("path/to/file.jpg", "rb") as f:
        file_content = f.read()

    # Create file input in JS and trigger upload
    page.evaluate("""([content, name]) => {
        const dt = new DataTransfer();
        const file = new File([new Uint8Array(content)], name, {type: 'image/jpeg'});
        dt.items.add(file);
        document.querySelector('.drop-zone').files = dt.files;
        document.querySelector('.drop-zone').dispatchEvent(new Event('change', { bubbles: true }));
    }""", [list(file_content), "test-image.jpg"])

    # Verify file was added
    expect(page.locator(".file-name")).to_contain_text("test-image.jpg")
```
