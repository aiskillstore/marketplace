# Column Name Matching and Normalization

## Basic Rules

- Perform normalization first: lowercase, trim leading/trailing spaces, replace spaces/hyphens with underscores
- Prioritize explicit alias mapping (alias -> target) to avoid over-reliance on fuzzy matching
- When multiple columns map to the same target column, use non-null priority merging and record conflicting columns

## Common Alias Examples

- first_name: firstname, first name, fname
- last_name: lastname, last name, lname
- email: e-mail, email_address
- phone: phone_number, tel, mobile
- company: organization, org

## Scenarios Requiring Manual Confirmation

- Multiple candidate columns have similar semantics but are uncertain (e.g., id vs. user_id)
- Column names are highly inconsistent with no reliable rules
- A single column may correspond to multiple target semantics (e.g., name could be full_name or company_name)