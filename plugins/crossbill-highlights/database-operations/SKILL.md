---
name: database-operations
description: Instructions on how to write database queries with SQLAlchemy.
---
When performing database operations using SQLAlchemy, follow these guidelines to ensure efficient and maintainable code:
- Avoid for-loops. Instead always prefer bulk operations using SQLAlchemy's built-in methods or use SQL joins to get related data in a single query.
- Database operations should be contained in repository classes
