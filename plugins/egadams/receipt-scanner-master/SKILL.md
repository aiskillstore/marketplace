---
name: Receipt Scanner Master
description: Master receipt scanning operations including parsing, debugging, enhancing accuracy, and database integration. Use when working with receipts, images, OCR issues, expense categorization, or troubleshooting receipt uploads.
---

# Receipt Scanner Master

Master the receipt scanning system that uses AI-powered OCR to extract structured data from receipt images and store them in the database.

## What This Skill Does

This skill helps you:
1. Parse receipt images (JPG, PNG, WebP, PDF) into structured data
2. Debug OCR accuracy issues and extraction errors
3. Enhance the receipt parsing engine and prompts
4. Test receipt uploads through the web interface
5. Troubleshoot database integration issues
6. Validate extracted data against actual receipts
7. Improve categorization and line item extraction

## System Architecture

### Frontend Components

**Receipt Scanner Component**: `/home/adamsl/planner/office-assistant/js/components/receipt-scanner.js`
- Primary receipt scanning interface at `http://localhost:8080/receipt-scanner.html`
- Drag-and-drop or file upload for receipt images
- Parses receipts and displays line items in a table
- **Each line item has a category-picker dropdown**
- **Items auto-save to database immediately when categorized**
- Only categorized items are saved (uncategorized items ignored)
- No overall receipt-level category picker (removed)

**Upload Component**: `/home/adamsl/planner/office-assistant/js/upload-component.js`
- Alternative upload interface (bank statements)
- Displays recent downloads from the system
- Shows real-time processing feedback via terminal display
- Handles streaming responses from backend (Server-Sent Events)
- Auto-refreshes file list after successful imports

### Backend Components

**Receipt Parser**: `app/services/receipt_parser.py`
- Validates file types and sizes
- Processes and compresses images
- Manages temporary and permanent file storage
- Coordinates with AI engine for extraction

**Receipt Engine**: `app/services/receipt_engine.py`
- Uses Google Gemini AI for OCR and extraction
- Implements strict accuracy validation rules
- Returns structured data via Pydantic models
- **Tries models in order: gemini-2.5-flash (first), 2.0-flash, 2.5-pro, pro-latest**
- Flash model used first to avoid pro quota limits
- Separate quotas for flash vs pro models

**API Endpoints**: `app/api/receipt_endpoints.py`
- `/api/parse-receipt` - Uploads and parses receipt image (returns temp data, doesn't save)
- `/api/receipt-items` - **Auto-saves individual line items when categorized**
- `/api/save-receipt` - Final save for categorized items (batch operation)
- `/api/receipts/{expense_id}` - Retrieves receipt metadata
- `/api/receipts/file/{year}/{month}/{filename}` - Serves stored receipt files

**Data Models**: `app/models/receipt_models.py`
- `ReceiptExtractionResult` - Complete receipt data structure
- `ReceiptItem` - Individual line items with categorization
- `ReceiptTotals` - Subtotal, tax, tip, discount, total
- `ReceiptPartyInfo` - Merchant details
- `ReceiptMeta` - Parsing metadata and model info
- `PaymentMethod` - Enum: CASH, CARD, BANK, OTHER

### Database Integration

**Tables**:
- `expenses` - Main expense entries (amount, date, category, method)
- `receipt_metadata` - Parsing metadata (model, confidence, raw response)

**Storage Structure**:
```
app/data/receipts/
├── YYYY/
│   ├── MM/
│   │   ├── receipt_TIMESTAMP_filename.jpg
│   │   └── receipt_TIMESTAMP_filename.pdf
└── temp/
    └── temp_receipt_TIMESTAMP_filename.jpg
```

## How to Use This Skill

### Step 1: Test Receipt Parsing

Parse a receipt image to extract structured data:

```bash
# Start the API server if not running
python3 api_server.py

# Test with curl (from another terminal)
curl -X POST "http://localhost:8000/api/parse-receipt" \
  -F "file=@/path/to/receipt.jpg"
```

**Expected Response**:
```json
{
  "parsed_data": {
    "transaction_date": "2025-01-15",
    "payment_method": "CARD",
    "party": {
      "merchant_name": "Walmart",
      "merchant_phone": null,
      "merchant_address": "123 Main St",
      "store_location": "Store #1234"
    },
    "items": [
      {
        "description": "MILK WHOLE GAL",
        "quantity": 1.0,
        "unit_price": 4.99,
        "line_total": 4.99
      }
    ],
    "totals": {
      "subtotal": 4.99,
      "tax_amount": 0.35,
      "tip_amount": 0.0,
      "discount_amount": 0.0,
      "total_amount": 5.34
    },
    "meta": {
      "currency": "USD",
      "receipt_number": "12345",
      "model_name": "gemini-2.5-pro"
    }
  },
  "temp_file_name": "temp_receipt_20250115T120000Z_receipt.jpg"
}
```

### Step 2: Debug OCR Accuracy Issues

When OCR produces incorrect amounts or descriptions:

**Common Issues**:
1. **Digit Confusion**: 4↔9, 3↔8, 5↔6, 0↔8, 1↔7
2. **Missing Items**: Items not extracted from receipt
3. **Wrong Totals**: Extracted amounts don't match
4. **Poor Image Quality**: Blurry, dark, or low-resolution images

**Debug Process**:

1. **Check the raw image quality**:
   ```bash
   # View the receipt image
   open /path/to/receipt.jpg
   # or
   xdg-open /path/to/receipt.jpg
   ```
   - Is text clearly readable?
   - Is image properly oriented?
   - Is there sufficient contrast?

2. **Review the Gemini prompt** in `app/services/receipt_engine.py:96-173`:
   - Look for the accuracy rules and verification steps
   - Check if new issue types need specific instructions
   - Verify digit confusion prevention rules are clear

3. **Test with higher quality image**:
   - Increase `RECEIPT_IMAGE_MAX_WIDTH_PX` in settings
   - Increase JPEG quality in `receipt_parser.py:80,83`

4. **Add validation logic**:
   - Check `quantity × unit_price = line_total` for each item
   - Verify `sum(line_totals) ≈ subtotal`
   - Compare `subtotal + tax - discount = total`

5. **Examine the raw AI response**:
   ```python
   # Add debug logging in receipt_engine.py:78
   print(f"Raw Gemini Response: {json_response}")
   ```

### Step 3: Enhance the Receipt Parser

To improve parsing accuracy and features:

**Modify the Gemini Prompt** (`app/services/receipt_engine.py`):

```python
def _get_prompt(self) -> str:
    return """
    You are an expert at extracting structured data from receipt images with EXTREME ACCURACY.

    [Add new instructions here, such as:]

    **NEW RULE**: For grocery store receipts, items often have:
    - Short codes (e.g., "VEG", "DAIRY", "MEAT")
    - Weight-based pricing (price per lb/kg)
    - Multi-buy discounts (e.g., "2 for $5")

    **VALIDATION ENHANCEMENT**: Before returning JSON:
    1. Verify every item's math: quantity × unit_price = line_total
    2. Sum all line_totals and compare to subtotal
    3. Check: subtotal + tax - discount + tip = total_amount
    4. If any validation fails, RE-EXAMINE the receipt more carefully

    ... [rest of prompt]
    """
```

**Improve Image Processing** (`app/services/receipt_parser.py`):

```python
async def _process_image(self, image_data: bytes, mime_type: str):
    if mime_type.startswith("image/"):
        img = Image.open(BytesIO(image_data))

        # Add preprocessing steps:
        # 1. Auto-rotate based on EXIF
        # 2. Increase contrast for faded receipts
        # 3. Sharpen slightly for better OCR
        # 4. Convert to grayscale if color isn't needed
```

**Add Custom Validation** (`app/api/receipt_endpoints.py`):

```python
@router.post("/parse-receipt")
async def parse_receipt_endpoint(file: UploadFile = File(...)):
    parsed_data, temp_file_name = await parser.process_receipt(file)

    # Add validation here:
    validation_errors = validate_receipt_data(parsed_data)
    if validation_errors:
        return JSONResponse(
            status_code=422,
            content={
                "errors": validation_errors,
                "parsed_data": parsed_data,
                "temp_file_name": temp_file_name
            }
        )

    return ParseReceiptResponse(...)
```

### Step 4: Test Through Web Interface

Test the complete workflow including UI:

1. **Start the API server**:
   ```bash
   cd /home/adamsl/planner/nonprofit_finance_db
   python3 api_server.py
   ```

2. **Open the web interface**:
   ```bash
   cd /home/adamsl/planner/office-assistant
   # Open index.html in browser or use a local server
   python3 -m http.server 8080
   # Navigate to http://localhost:8080
   ```

3. **Test the upload flow**:
   - Download a test receipt (PDF or image) to ~/Downloads
   - Verify it appears in the upload component
   - Select the receipt and click "Import Selected PDF"
   - Watch the terminal output for processing steps
   - Verify success message and database insertion

4. **Check database entries**:
   ```bash
   # Connect to database and verify
   mysql -u root -p nonprofit_finance_db
   ```
   ```sql
   -- Check latest expense entries
   SELECT * FROM expenses ORDER BY id DESC LIMIT 5;

   -- Check receipt metadata
   SELECT * FROM receipt_metadata ORDER BY id DESC LIMIT 5;

   -- Verify file storage
   SELECT expense_id, receipt_url FROM expenses WHERE receipt_url IS NOT NULL LIMIT 5;
   ```

### Step 5: Troubleshoot Database Issues

Common database integration problems:

**Issue**: Receipt parsed but not saved to database

**Debug steps**:
```bash
# Check API server logs
tail -f api_server.log

# Look for errors in save_receipt_endpoint
grep -A 10 "Error saving expense" api_server.log

# Verify database connection
python3 -c "from app.repositories.expenses import ExpenseRepository; repo = ExpenseRepository(); print('Connection OK')"
```

**Issue**: File saved to temp but not moved to permanent storage

**Debug steps**:
```bash
# Check temp directory
ls -lth app/data/receipts/temp/ | head -20

# Check permanent storage structure
ls -R app/data/receipts/ | grep -E "^\\./"

# Verify permissions
ls -ld app/data/receipts/
```

**Issue**: Categorization not working

**Debug steps**:
```bash
# Check categories table
mysql -u root -p -e "SELECT id, name, category_path FROM categories ORDER BY id;" nonprofit_finance_db

# Verify category_id assignments in parsed items
# Items without category_id are not saved to database
```

### Step 6: Validate Extraction Accuracy

Manually verify OCR accuracy:

1. **Get the parsed data**:
   ```bash
   curl -X POST "http://localhost:8000/api/parse-receipt" \
     -F "file=@receipt.jpg" | jq '.'
   ```

2. **Compare against actual receipt**:
   - Open receipt image side-by-side
   - Check each line item: description, quantity, price, total
   - Verify merchant name and address
   - Confirm tax amount and final total
   - Note any discrepancies

3. **Calculate accuracy metrics**:
   ```python
   # Create a validation script
   import json

   def validate_receipt(parsed_json, actual_receipt_data):
       errors = []

       # Check item count
       if len(parsed_json['items']) != len(actual_receipt_data['items']):
           errors.append(f"Item count mismatch: {len(parsed_json['items'])} vs {len(actual_receipt_data['items'])}")

       # Check each item
       for i, (parsed, actual) in enumerate(zip(parsed_json['items'], actual_receipt_data['items'])):
           if parsed['line_total'] != actual['line_total']:
               errors.append(f"Item {i}: ${parsed['line_total']} vs ${actual['line_total']}")

       # Check total
       if parsed_json['totals']['total_amount'] != actual_receipt_data['total']:
           errors.append(f"Total: ${parsed_json['totals']['total_amount']} vs ${actual_receipt_data['total']}")

       return errors
   ```

## Configuration Files

**Environment Variables** (`.env`):
```bash
GEMINI_API_KEY=your_gemini_api_key_here

# Receipt settings
RECEIPT_MAX_SIZE_MB=10
RECEIPT_IMAGE_MAX_WIDTH_PX=2048
RECEIPT_IMAGE_MAX_HEIGHT_PX=2048
RECEIPT_PARSE_TIMEOUT_SECONDS=30
RECEIPT_UPLOAD_DIR=app/data/receipts
RECEIPT_TEMP_UPLOAD_DIR=app/data/receipts/temp
```

**Settings** (`app/config.py`):
```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str
    RECEIPT_MAX_SIZE_MB: int = 10
    RECEIPT_IMAGE_MAX_WIDTH_PX: int = 1024
    RECEIPT_IMAGE_MAX_HEIGHT_PX: int = 1024
    RECEIPT_PARSE_TIMEOUT_SECONDS: int = 30
    RECEIPT_UPLOAD_DIR: str = "app/data/receipts"
    RECEIPT_TEMP_UPLOAD_DIR: str = "app/data/receipts/temp"
```

## Receipt Scanner Workflow (Important!)

**CRITICAL**: Items do NOT automatically save when you scan a receipt. You must categorize items for them to be saved.

### Workflow Steps:

1. **Upload receipt** → Parses and shows line items (nothing saved yet)
2. **Select category for each item** → **Item saves immediately to database**
3. **"Save Expense" button** → Optional final confirmation

### What Gets Saved:

- ✓ Items with categories selected → Saved to `expenses` table
- ✗ Items without categories → Ignored, not saved
- Each categorized item becomes a separate expense entry

### Database Behavior:

```javascript
// When you select a category for an item:
_persistCategorizedItem(index, categoryId) {
  // Immediately POSTs to /api/receipt-items
  // Creates expense entry in database
  // Returns expense_id for the item
}
```

## Common Issues & Solutions

### Issue: "GEMINI_API_KEY environment variable not set"

**Solution**:
```bash
# Add to .env file
echo 'GEMINI_API_KEY=your_key_here' >> .env

# Or export in current session
export GEMINI_API_KEY=your_key_here
```

### Issue: Gemini API quota exceeded (429 error)

**Root Cause**: Hit the free tier daily quota for a specific model

**Solutions**:
1. **Model fallback** (already implemented):
   - Receipt engine tries flash models first (separate quota from pro)
   - Order: gemini-2.5-flash → 2.0-flash → 2.5-pro → pro-latest

2. **Wait for quota reset** (24 hours)

3. **Use different Google account**:
   - Create API key from different account
   - Update GEMINI_API_KEY in `.env`

4. **Upgrade to paid tier** (higher quotas)

### Issue: OCR reads $4.99 as $9.99

**Root Cause**: Digit confusion (4 vs 9)

**Solution**: Enhance Gemini prompt with specific digit rules:
```python
**DIGIT 4 vs 9 RECOGNITION**:
- 4 has sharp angles, often looks like "4" with a horizontal line and vertical line meeting
- 9 has a curved top, looks like "g" or "q" without the tail
- Context check: grocery items rarely cost $9.99, more often $4.99
```

### Issue: Missing line items in extraction

**Root Cause**: Items at bottom of receipt or spanning multiple lines

**Solution**:
1. Increase image resolution in `receipt_parser.py`
2. Add instruction to Gemini prompt:
   ```
   **COMPLETE EXTRACTION**: Extract ALL items from top to bottom of receipt.
   Do not skip items even if they are:
   - At the very bottom of the receipt
   - Spanning multiple lines
   - In a different format or font
   ```

### Issue: Tax calculation mismatch

**Root Cause**: Some items are tax-exempt or have different tax rates

**Solution**:
- Add per-item tax tracking in `ReceiptItem` model
- Update Gemini prompt to identify taxable vs non-taxable items
- Validate: `sum(item.tax_amount for item in items) = totals.tax_amount`

### Issue: "Receipt parsing exceeded 30 seconds"

**Root Cause**: Large image file or slow API response

**Solutions**:
```python
# Increase timeout in settings
RECEIPT_PARSE_TIMEOUT_SECONDS=60

# Reduce image size before sending to API
# In receipt_parser.py, decrease max dimensions
max_width = 1024  # Instead of 2048
max_height = 1024
```

### Issue: Uploaded file not appearing in component

**Root Cause**: Frontend not polling or backend endpoint error

**Debug steps**:
```bash
# Check backend endpoint
curl http://localhost:8000/api/recent-downloads

# Check frontend console
# Open browser DevTools → Console → look for errors

# Verify file in Downloads folder
ls -lth ~/Downloads/*.pdf | head -5
```

## Key Files Reference

### Backend Files
- `app/services/receipt_parser.py` - Main parsing logic
- `app/services/receipt_engine.py` - AI engine integration
- `app/api/receipt_endpoints.py` - REST API endpoints
- `app/models/receipt_models.py` - Data models
- `app/repositories/receipt_metadata.py` - Metadata storage
- `app/repositories/expenses.py` - Expense storage
- `app/config.py` - Configuration settings

### Frontend Files
- `/home/adamsl/planner/office-assistant/js/upload-component.js` - Upload UI component
- `/home/adamsl/planner/office-assistant/js/app.js` - Main application
- `/home/adamsl/planner/office-assistant/js/category-picker.js` - Category selection

### Test Files
- `tests/test_receipt_processing.py` - Receipt processing tests
- `tests/test_receipt_items_api.py` - API endpoint tests
- `test_receipt_api.py` - Integration tests

## Examples

### Example 1: Scan and Categorize a Receipt (Web Interface)

User request:
```
I want to scan my Meijer receipt and categorize the groceries
```

You would:
1. Direct user to the receipt scanner:
   ```
   Open http://localhost:8080/receipt-scanner.html in your browser
   ```

2. Guide the workflow:
   - **Upload**: Drag and drop the receipt image or click to browse
   - **Wait**: Receipt parses automatically (gemini-2.5-flash model)
   - **Review**: Check the parsed line items in the table
   - **Categorize**: Select category for each item you want to track
     - Click category dropdown for each item
     - Select appropriate category (e.g., "Groceries > Dairy")
     - **Item saves immediately to database**
   - **Optional**: Click "Save Expense" to confirm completion

3. Verify in database:
   - Only categorized items are saved
   - Each item is a separate expense entry
   - Uncategorized items are ignored

4. View in Daily Expense Categorizer:
   - Navigate to `http://localhost:8080/daily_expense_categorizer.html`
   - Select the month from dropdown
   - Select the date
   - See all saved receipt items
   - Can re-categorize if needed

### Example 2: Parse a Grocery Receipt (API)

User request:
```
Parse this grocery receipt via API and extract all items with prices
```

You would:
1. Verify API server is running:
   ```bash
   ps aux | grep api_server.py
   # If not running: python3 api_server.py
   ```

2. Parse the receipt:
   ```bash
   curl -X POST "http://localhost:8080/api/parse-receipt" \
     -F "file=@grocery_receipt.jpg" | jq '.'
   ```

3. Review the output:
   - Check `items[]` array for all products
   - Verify `totals.total_amount` matches receipt
   - Note the `temp_file_name` for saving later
   - **Note: Nothing is saved to database yet**

4. If items are missing:
   - Open the receipt image and compare
   - Check if image quality is sufficient
   - Look for items at bottom or in different sections

### Example 3: Debug OCR Misreading Prices

User request:
```
The receipt parser is reading $4.99 items as $9.99
```

You would:
1. Reproduce the issue:
   ```bash
   curl -X POST "http://localhost:8000/api/parse-receipt" \
     -F "file=@problem_receipt.jpg" > parsed_output.json

   # Compare parsed vs actual
   cat parsed_output.json | jq '.parsed_data.items[] | {description, unit_price}'
   ```

2. Read the current Gemini prompt:
   ```bash
   grep -A 30 "DIGIT CONFUSION PREVENTION" app/services/receipt_engine.py
   ```

3. Enhance the prompt with specific 4 vs 9 rules:
   ```python
   # In receipt_engine.py, _get_prompt() method
   **CRITICAL: DIGIT 4 vs DIGIT 9**:
   - When you see what might be 4 or 9, examine the top of the digit
   - 4: Angular top, horizontal line going right
   - 9: Curved/circular top, like the letter "g"
   - Common grocery prices: $4.99, $14.99, NOT $9.99, $19.99
   - If unsure, default to 4 for items under $10
   ```

4. Test with the problematic receipt:
   ```bash
   # Restart server to load new prompt
   pkill -f api_server.py
   python3 api_server.py &

   # Re-test
   curl -X POST "http://localhost:8000/api/parse-receipt" \
     -F "file=@problem_receipt.jpg" | jq '.parsed_data.items[].unit_price'
   ```

5. Verify improvement and test with other receipts

### Example 4: Add Custom Validation

User request:
```
Validate that line totals match quantity times price
```

You would:
1. Read the current endpoint code:
   ```bash
   cat app/api/receipt_endpoints.py | grep -A 20 "parse_receipt_endpoint"
   ```

2. Create a validation function:
   ```python
   # Add to receipt_endpoints.py
   def validate_receipt_math(parsed_data: ReceiptExtractionResult) -> List[str]:
       errors = []

       for i, item in enumerate(parsed_data.items):
           expected_total = round(item.quantity * item.unit_price, 2)
           if abs(expected_total - item.line_total) > 0.01:
               errors.append(
                   f"Item {i} '{item.description}': "
                   f"{item.quantity} × ${item.unit_price} = ${expected_total}, "
                   f"but line_total is ${item.line_total}"
               )

       # Validate subtotal
       items_sum = sum(item.line_total for item in parsed_data.items)
       if abs(items_sum - parsed_data.totals.subtotal) > 0.50:
           errors.append(
               f"Items sum to ${items_sum:.2f} but subtotal is ${parsed_data.totals.subtotal:.2f}"
           )

       # Validate final total
       calculated_total = (
           parsed_data.totals.subtotal +
           (parsed_data.totals.tax_amount or 0) +
           (parsed_data.totals.tip_amount or 0) -
           (parsed_data.totals.discount_amount or 0)
       )
       if abs(calculated_total - parsed_data.totals.total_amount) > 0.01:
           errors.append(
               f"Calculated total ${calculated_total:.2f} != stated total ${parsed_data.totals.total_amount:.2f}"
           )

       return errors
   ```

3. Integrate validation into endpoint:
   ```python
   @router.post("/parse-receipt", response_model=ParseReceiptResponse)
   async def parse_receipt_endpoint(file: UploadFile = File(...)):
       parser = get_receipt_parser()
       temp_file_name: Optional[str] = None
       try:
           parsed_data, temp_file_name = await parser.process_receipt(file)

           # Add validation
           validation_errors = validate_receipt_math(parsed_data)
           if validation_errors:
               # Log errors but still return the data
               print(f"Validation warnings: {validation_errors}")

           return ParseReceiptResponse(parsed_data=parsed_data, temp_file_name=temp_file_name)
   ```

4. Test the validation:
   ```bash
   # Use a receipt with known correct totals
   curl -X POST "http://localhost:8000/api/parse-receipt" \
     -F "file=@test_receipt_good.jpg"

   # Use a receipt with deliberate errors (or mock the data)
   # Check logs for validation warnings
   tail -f api_server.log
   ```

### Example 5: Integrate with Letta Agent

User request:
```
Make Letta able to scan and categorize receipts
```

You would:
1. Ensure this skill is available to Letta:
   ```bash
   # Skill already in .claude/skills/receipt-scanner/
   # Letta can invoke Claude Code skills via agent tool calls
   ```

2. Create a Letta tool function:
   ```python
   # In letta_agent/tools/receipt_tools.py
   from typing import Optional
   import httpx

   @tool
   def scan_receipt(image_path: str) -> dict:
       """
       Scan a receipt image and extract structured data.

       Args:
           image_path: Path to the receipt image file

       Returns:
           Dictionary with merchant, items, totals, and metadata
       """
       with open(image_path, 'rb') as f:
           files = {'file': f}
           response = httpx.post(
               'http://localhost:8000/api/parse-receipt',
               files=files,
               timeout=60.0
           )

       if response.status_code == 200:
           return response.json()
       else:
           return {'error': response.text}
   ```

3. Register the tool with Letta agent:
   ```python
   # In hybrid_letta_persistent.py
   from letta_agent.tools.receipt_tools import scan_receipt

   agent = client.create_agent(
       name="finance_assistant",
       tools=[scan_receipt, ...],
       ...
   )
   ```

4. Test with Letta:
   ```python
   # Chat with Letta
   response = client.send_message(
       agent_id=agent.id,
       message="Scan the receipt at ~/Downloads/walmart_receipt.jpg and tell me the total"
   )
   print(response)
   ```

## Success Criteria

The skill is successful when:
- Receipts parse with >95% accuracy on item prices
- All line items are extracted (no missing items)
- Totals match within $0.01 tolerance
- Database integration works consistently
- Web interface provides clear feedback
- Common OCR issues have documented solutions
- Letta agents can successfully use receipt scanning

## Tips for Users

1. **Start with high-quality images**: Clear, well-lit, straight photos work best
2. **Test incrementally**: Parse → validate → save (don't skip validation)
3. **Build validation suite**: Collect problematic receipts and test regularly
4. **Monitor accuracy trends**: Track OCR errors to identify patterns
5. **Update prompt iteratively**: Add specific rules as you encounter issues
6. **Use streaming responses**: Enable real-time feedback for better UX
7. **Backup original files**: Keep original receipts even after successful parsing
