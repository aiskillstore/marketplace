# Receipt Scanning Tools Skill

## Project Overview

This skill helps you work with the receipt scanning tools in the nonprofit_finance_db project. It includes manual entry tools, automated OCR scanning, and database integration for tracking receipts and expenses.

## Critical Project Paths

### Virtual Environment
```bash
# Virtual environment location (IMPORTANT!)
VENV_PATH=/home/adamsl/planner/.venv

# Always activate before running Python scripts:
source /home/adamsl/planner/.venv/bin/activate
```

### Project Root
```bash
PROJECT_ROOT=/home/adamsl/planner/nonprofit_finance_db
```

### Receipt Scanning Tools Directory
```bash
TOOLS_DIR=/home/adamsl/planner/nonprofit_finance_db/receipt_scanning_tools
```

### Key Files

**Receipt Tools:**
- `receipt_scanning_tools/receipt_tools_menu.py` - **Main menu** for all receipt tools
- `receipt_scanning_tools/manual_entry.py` - Manual receipt entry CLI tool
- `receipt_scanning_tools/delete_expenses_by_date.py` - Delete expenses by date tool

**Backend Services:**
- `app/services/receipt_parser.py` - Receipt parsing service
- `app/services/receipt_engine.py` - AI-powered OCR engine
- `app/api/receipt_endpoints.py` - REST API endpoints
- `app/models/receipt_models.py` - Data models
- `app/db/pool.py` - Database connection pool

## Database Schema

### Categories Table
```sql
-- Actual schema (no category_path column!)
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    parent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- To get full category path, use recursive query:
WITH RECURSIVE category_hierarchy AS (
    SELECT id, name, parent_id, name as full_path
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id,
           CONCAT(ch.full_path, ' > ', c.name) as full_path
    FROM categories c
    INNER JOIN category_hierarchy ch ON c.parent_id = ch.id
)
SELECT * FROM category_hierarchy ORDER BY full_path;
```

### Merchants Table
```sql
CREATE TABLE merchants (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_category (category)
);

-- Categories for church non-profit:
-- Gifts and Love Offerings: Guiding Light, Mel Trotter Ministries,
--                            Salvation Army, Samaritan Purse, Jews for Jesus,
--                            Intercessors for America, Segals in Israel,
--                            Chosen People, Columbia Orphanage, Right to Life,
--                            Johnsons in Dominican Republic, Jewish Voice
-- Ministers and Workers: EG Adams, Snowplow Person
-- Presents for ROL Friends and Members: James Abney, Cliff Baker, Annie Baker,
--                                        Karen Cook, Richard Meninga, Karen Roark,
--                                        Hannah Schneider, Rebecca Esposito,
--                                        Karen Vander Vliet, Mark Vander Vliet,
--                                        Alexander Vander Vliet, John Roark,
--                                        Joshua McKay, Eddie Hoekstra, Ian Gonzalez
-- Food & Supplies: Meijer, Gordon Foods, Walmart, Target, Costco,
--                  Sams Club, Kroger, Aldi, Family Fare, Spartan Stores
```

### Expenses Table
```sql
CREATE TABLE expenses (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    org_id BIGINT UNSIGNED NOT NULL,
    expense_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    category_id BIGINT UNSIGNED,
    merchant_id BIGINT UNSIGNED,  -- Links to merchants table
    method ENUM('CASH','CARD','BANK','OTHER'),
    description VARCHAR(255),
    receipt_url VARCHAR(500),
    paid_by_contact_id BIGINT UNSIGNED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
);
```

### Receipt Metadata Table
```sql
CREATE TABLE receipt_metadata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    expense_id INT NOT NULL,
    model_name VARCHAR(100),
    confidence_score DECIMAL(3,2),
    raw_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expense_id) REFERENCES expenses(id)
);
```

## Common Commands

### Database Inspection
```bash
# Connect to database (with venv activated)
source /home/adamsl/planner/.venv/bin/activate
cd /home/adamsl/planner/nonprofit_finance_db

# Check categories structure
python3 -c "
from app.db import get_connection
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('DESCRIBE categories')
    for row in cursor.fetchall():
        print(row)
"

# View categories with hierarchy
python3 -c "
from app.db import get_connection
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('''
        WITH RECURSIVE category_hierarchy AS (
            SELECT id, name, parent_id, name as full_path, 0 as level
            FROM categories
            WHERE parent_id IS NULL
            UNION ALL
            SELECT c.id, c.name, c.parent_id,
                   CONCAT(ch.full_path, \" > \", c.name) as full_path,
                   ch.level + 1
            FROM categories c
            INNER JOIN category_hierarchy ch ON c.parent_id = ch.id
        )
        SELECT id, name, full_path FROM category_hierarchy ORDER BY full_path
    ''')
    for row in cursor.fetchall():
        print(f'{row[0]:3d} | {row[1]:30s} | {row[2]}')
"
```

### Running Tools
```bash
# Always activate venv first!
source /home/adamsl/planner/.venv/bin/activate
cd /home/adamsl/planner/nonprofit_finance_db

# Run main receipt tools menu (RECOMMENDED)
python3 receipt_scanning_tools/receipt_tools_menu.py

# Or run individual tools directly:
python3 receipt_scanning_tools/manual_entry.py
python3 receipt_scanning_tools/delete_expenses_by_date.py

# Other services:
python3 api_server.py  # API server
python3 scripts/view_transactions.py  # Transaction viewer
```

## Typical Workflows

### Workflow 1: Manual Receipt Entry
1. Activate virtual environment
2. Run manual entry tool
3. **Select merchant from categorized menu**:
   - **Gifts and Love Offerings** (12 ministries: Guiding Light, Mel Trotter, Salvation Army, Samaritan Purse, Jews for Jesus, etc.)
   - **Ministers and Workers** (2 people: EG Adams, Snowplow Person)
   - **Presents for ROL Friends and Members** (15 people: James Abney, Baker family, Karen Cook, etc.)
   - **Food & Supplies** (grocery stores: Meijer, Gordon Foods, Walmart, etc.)
   - Option to add custom merchant with category
4. Enter receipt amount and date
5. Select expense category from hierarchical list
6. Review summary and confirm
7. Save to database

**Merchant Selection Features:**
- **Organized by category** for church non-profit giving and ministry
- Pre-populated with actual ministry partners and recipients
- Separate categories for love offerings, worker support, and member gifts
- Option to add custom merchant names with category selection (5 categories)
- Merchants stored in database for reuse across entries
- Alphabetically sorted within each category

### Workflow 2: Fix Schema Issues
When you encounter column errors like "Unknown column 'category_path'":

1. Check actual table schema:
   ```python
   from app.db import get_connection
   with get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute('DESCRIBE categories')
       print(cursor.fetchall())
   ```

2. Update query to use actual columns
3. Use recursive CTE for hierarchical path if needed

### Workflow 3: Add New Receipt Scanning Tool
1. Create new Python file in `receipt_scanning_tools/`
2. Import database connection: `from app.db import get_connection`
3. Use Rich library for CLI formatting
4. Follow pattern from `manual_entry.py`
5. Make executable: `chmod +x receipt_scanning_tools/your_tool.py`

## Environment Configuration

### Database Connection
```bash
# Environment variables in .env file
DB_HOST=127.0.0.1
DB_PORT=3306
NON_PROFIT_USER=adamsl
NON_PROFIT_PASSWORD=<password>
NON_PROFIT_DB_NAME=nonprofit_finance
```

### API Keys
```bash
# For AI-powered OCR
GEMINI_API_KEY=<your_key>
```

## Code Patterns

### Getting Merchants
```python
from app.db import get_connection

def get_merchants():
    """Fetch merchants from database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, category
            FROM merchants
            ORDER BY name
        """)
        return cursor.fetchall()
```

### Adding a New Merchant
```python
from app.db import get_connection

def add_merchant(name, category="Food & Supplies"):
    """Add a new merchant to the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO merchants (name, category)
            VALUES (%s, %s)
        """, (name, category))
        conn.commit()
        return cursor.lastrowid
```

### Getting Categories with Full Path
```python
from app.db import get_connection

def get_categories_with_path():
    """Fetch categories with full hierarchical path"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            WITH RECURSIVE category_hierarchy AS (
                SELECT id, name, parent_id, name as full_path
                FROM categories
                WHERE parent_id IS NULL
                UNION ALL
                SELECT c.id, c.name, c.parent_id,
                       CONCAT(ch.full_path, ' > ', c.name) as full_path
                FROM categories c
                INNER JOIN category_hierarchy ch ON c.parent_id = ch.id
            )
            SELECT id, name, full_path
            FROM category_hierarchy
            ORDER BY full_path
        """)
        return cursor.fetchall()
```

### Saving an Expense
```python
from app.db import get_connection
from datetime import datetime

def save_expense(org_id, date, amount, category_id, description):
    """Save expense to database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (
                org_id, expense_date, amount, category_id,
                payment_method, description, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            org_id,
            date,
            amount,
            category_id,
            "CASH",
            description,
            datetime.now()
        ))
        conn.commit()
        return cursor.lastrowid
```

### Using Rich for CLI Output
```python
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, Confirm
from rich import box

console = Console()

# Display table
table = Table(box=box.ROUNDED, show_header=True)
table.add_column("ID", style="cyan")
table.add_column("Name", style="yellow")
table.add_row("1", "Groceries")
console.print(table)

# Get user input
amount = FloatPrompt.ask("Enter amount")
confirm = Confirm.ask("Save this?")
```

## Troubleshooting

### Issue: "Unknown column 'category_path'"
**Cause**: Query assumes column that doesn't exist in schema
**Fix**: Use recursive CTE to build hierarchical path, or just use `name` column

### Issue: "ModuleNotFoundError: No module named 'mysql'"
**Cause**: Virtual environment not activated
**Fix**: `source /home/adamsl/planner/.venv/bin/activate`

### Issue: "No categories found"
**Cause**: Database not initialized or connection failed
**Fix**:
1. Check DB connection settings in `.env`
2. Run database initialization: `python3 scripts/init_db.py`
3. Check if MySQL server is running

### Issue: Import errors from `app.*` modules
**Cause**: Wrong working directory or Python path
**Fix**:
```python
# Add to top of script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

## Testing Commands

### Quick Database Check
```bash
source /home/adamsl/planner/.venv/bin/activate
cd /home/adamsl/planner/nonprofit_finance_db
python3 -c "from app.db import get_connection; print('✓ Database connection OK')"
```

### List Recent Expenses
```bash
python3 -c "
from app.db import get_connection
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT id, expense_date, amount, description FROM expenses ORDER BY id DESC LIMIT 5')
    for row in cursor.fetchall():
        print(row)
"
```

### Count Categories
```bash
python3 -c "
from app.db import get_connection
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM categories')
    print(f'Total categories: {cursor.fetchone()[0]}')
"
```

## Best Practices

1. **Always activate virtual environment first** - Most import errors come from forgetting this
2. **Check schema before writing queries** - Don't assume column names
3. **Use context managers for DB connections** - Ensures proper cleanup
4. **Validate user input** - Especially dates and amounts
5. **Provide clear error messages** - Help users understand what went wrong
6. **Use Rich library for CLI** - Makes tools more user-friendly
7. **Test with small data first** - Before processing large batches

## Next Steps / TODO

- [x] Create merchants table for storing common merchants
- [x] Add merchant selection menu (smart menu style)
- [x] Update manual entry to use merchant selection
- [x] Create main menu for receipt scanning tools
- [x] Add delete expenses by date tool
- [x] Add view recent expenses feature
- [x] Add basic merchant management
- [ ] Add receipt image upload tool
- [ ] Integrate OCR scanning with manual entry
- [ ] Add bulk import from CSV
- [ ] Create receipt preview/validation tool
- [ ] Add advanced merchant management (edit, delete)
- [ ] Add category management CLI
- [ ] Build receipt search/filter tool
