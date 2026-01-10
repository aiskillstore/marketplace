---
name: sqlmodel-crud
description: |
  Use when creating SQLModel database models, CRUD operations, queries with joins, or relationships.
  NOT when non-database operations, plain SQL, or unrelated data handling.
  Triggers: "SQLModel", "database model", "CRUD", "create/read/update/delete", "query", "ForeignKey", "relationship".
---

# SQLModel CRUD Skill

## Overview

Expert guidance for SQLModel database models and CRUD operations, including Pydantic integration, async session management, query building with joins, and relationship configuration for ERP entities like Student, Fee, and Attendance.

## When This Skill Applies

This skill triggers when users request:
- **Models**: "Student model", "SQLModel", "database model", "table=True"
- **CRUD Operations**: "Create student", "Read fees", "Update attendance", "Delete record"
- **Query Building**: "Query with join", "select statement", "where clause", "pagination"
- **Relationships**: "ForeignKey", "back_populates", "relationship", "linked models"
- **Validation**: "Pydantic validators", "field constraints", "indexes"

## Core Rules

### 1. Models: table=True with Pydantic Validation

```python
# models/student.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class StudentRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class Student(SQLModel, table=True):
    """Student model with relationships to fees and attendance"""
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=100, index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(default=None, pattern=r'^\+?[\d\s-]+$')
    password_hash: str
    role: StudentRole = Field(default=StudentRole.STUDENT)
    class_id: Optional[str] = Field(default=None, foreign_key="class.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    class_obj: Optional["Class"] = Relationship(back_populates="students")
    fees: List["Fee"] = Relationship(back_populates="student")
    attendance: List["Attendance"] = Relationship(back_populates="student")

    class Config:
        from_attributes = True

class Class(SQLModel, table=True):
    """Class model for organizing students"""
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=50)
    grade_level: int = Field(ge=1, le=12)
    academic_year: str = Field(max_length=9, pattern=r'^\d{4}-\d{4}$')
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    students: List[Student] = Relationship(back_populates="class_obj")

class Fee(SQLModel, table=True):
    """Fee model linked to students"""
    id: Optional[str] = Field(default=None, primary_key=True)
    student_id: str = Field(foreign_key="student.id", index=True)
    amount: float = Field(gt=0)
    description: str = Field(max_length=500)
    status: str = Field(default="pending", pattern=r'^(pending|paid|overdue|waived)$')
    due_date: datetime
    paid_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Optional[Student] = Relationship(back_populates="fees")

class Attendance(SQLModel, table=True):
    """Attendance model linked to students"""
    id: Optional[str] = Field(default=None, primary_key=True)
    student_id: str = Field(foreign_key="student.id", index=True)
    date: datetime = Field(index=True)
    status: str = Field(pattern=r'^(present|absent|late|excused)$')
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Optional[Student] = Relationship(back_populates="attendance")
```

**Requirements:**
- Use `table=True` for database tables
- Add `index=True` for frequently queried fields
- Use `unique=True` for email and other unique fields
- Add `foreign_key` for relationships
- Use Pydantic validators (min_length, max_length, pattern, ge, gt)
- Use `Relationship` with `back_populates` for bidirectional links
- Include `created_at` and `updated_at` timestamps

### 2. CRUD Operations: Async Session Management

```python
# crud/student.py
from sqlmodel import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from models.student import Student
from schemas.student import StudentCreate, StudentUpdate

class StudentCRUD:
    """CRUD operations for Student model"""

    @staticmethod
    async def create(db: AsyncSession, student_data: StudentCreate) -> Student:
        """Create a new student"""
        student = Student(
            name=student_data.name,
            email=student_data.email,
            phone=student_data.phone,
            password_hash=student_data.password_hash,
            role=student_data.role,
            class_id=student_data.class_id,
        )
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    @staticmethod
    async def get_by_id(db: AsyncSession, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[Student]:
        """Get student by email"""
        result = await db.execute(
            select(Student).where(Student.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        class_id: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[Student]:
        """Get all students with pagination and filters"""
        query = select(Student)

        if class_id:
            query = query.where(Student.class_id == class_id)
        if role:
            query = query.where(Student.role == role)

        query = query.offset(skip).limit(limit).order_by(Student.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update(
        db: AsyncSession,
        student_id: str,
        student_data: StudentUpdate,
    ) -> Optional[Student]:
        """Update a student"""
        student = await StudentCRUD.get_by_id(db, student_id)
        if not student:
            return None

        update_data = student_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)

        student.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(student)
        return student

    @staticmethod
    async def delete(db: AsyncSession, student_id: str) -> bool:
        """Delete a student"""
        student = await StudentCRUD.get_by_id(db, student_id)
        if not student:
            return False

        await db.delete(student)
        await db.commit()
        return True

    @staticmethod
    async def count(
        db: AsyncSession,
        class_id: Optional[str] = None,
        role: Optional[str] = None,
    ) -> int:
        """Count students with filters"""
        query = select(Student)

        if class_id:
            query = query.where(Student.class_id == class_id)
        if role:
            query = query.where(Student.role == role)

        result = await db.execute(query)
        return len(result.scalars().all())
```

**Requirements:**
- Use `AsyncSession` for async database operations
- Use `select()`, `where()`, `offset()`, `limit()`, `order_by()`
- Return `Optional[T]` for single items, `List[T]` for lists
- Use `scalar_one_or_none()` for single results
- Use `scalars().all()` for list results
- Handle transactions with commit/rollback
- Update `updated_at` timestamp on modifications

### 3. Query Building: Joins, Filters, Pagination

```python
# queries/advanced.py
from sqlmodel import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models.student import Student, Fee, Attendance, Class

class StudentQueries:
    """Advanced student queries with joins"""

    @staticmethod
    async def get_student_with_fees(
        db: AsyncSession,
        student_id: str,
    ) -> Optional[Student]:
        """Get student with all their fees"""
        result = await db.execute(
            select(Student)
            .where(Student.id == student_id)
            .options(
                # Eager load fees relationship
                selectinload(Student.fees)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_students_with_pending_fees(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Student]:
        """Get students with pending fee balance"""
        # Subquery to find students with pending fees
        subquery = (
            select(Fee.student_id)
            .where(Fee.status == "pending")
            .distinct()
        )

        result = await db.execute(
            select(Student)
            .where(Student.id.in_(subquery))
            .offset(skip)
            .limit(limit)
            .order_by(Student.name)
        )
        return result.scalars().all()

    @staticmethod
    async def get_student_attendance_summary(
        db: AsyncSession,
        student_id: str,
        month: int,
        year: int,
    ) -> dict:
        """Get attendance summary for a student in a month"""
        from datetime import datetime

        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        result = await db.execute(
            select(
                func.count().label("total_days"),
                func.sum(
                    case((Attendance.status == "present", 1), else_=0)
                ).label("present_days"),
                func.sum(
                    case((Attendance.status == "absent", 1), else_=0)
                ).label("absent_days"),
                func.sum(
                    case((Attendance.status == "late", 1), else_=0)
                ).label("late_days"),
            )
            .where(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.date >= start_date,
                    Attendance.date < end_date,
                )
            )
        )
        row = result.one()
        return {
            "total_days": row.total_days or 0,
            "present_days": row.present_days or 0,
            "absent_days": row.absent_days or 0,
            "late_days": row.late_days or 0,
        }

    @staticmethod
    async def search_students(
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Student]:
        """Search students by name or email"""
        search_pattern = f"%{search_term}%"

        result = await db.execute(
            select(Student)
            .where(
                or_(
                    Student.name.ilike(search_pattern),
                    Student.email.ilike(search_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Student.name)
        )
        return result.scalars().all()

    @staticmethod
    async def get_students_by_class(
        db: AsyncSession,
        class_id: str,
        include_inactive: bool = False,
    ) -> List[Student]:
        """Get all students in a class"""
        query = select(Student).where(Student.class_id == class_id)

        if not include_inactive:
            # Assuming there's an is_active field
            query = query.where(Student.is_active == True)

        query = query.order_by(Student.name)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_fee_statistics(
        db: AsyncSession,
        class_id: Optional[str] = None,
    ) -> dict:
        """Get fee statistics, optionally filtered by class"""
        base_query = select(Fee)

        if class_id:
            # Join with Student to filter by class
            base_query = (
                select(Fee)
                .join(Student, Student.id == Fee.student_id)
                .where(Student.class_id == class_id)
            )

        result = await db.execute(
            select(
                func.count().label("total_fees"),
                func.sum(Fee.amount).label("total_amount"),
                func.sum(
                    case((Fee.status == "paid", Fee.amount), else_=0)
                ).label("total_collected"),
                func.sum(
                    case((Fee.status == "pending", Fee.amount), else_=0)
                ).label("total_pending"),
            )
        )
        row = result.one()
        return {
            "total_fees": row.total_fees or 0,
            "total_amount": float(row.total_amount or 0),
            "total_collected": float(row.total_collected or 0),
            "total_pending": float(row.total_pending or 0),
        }
```

**Requirements:**
- Use `selectinload()` for eager loading relationships
- Use `subquery` for complex filtering
- Use `and_()`/`or_()` for compound conditions
- Use `func.count()`, `func.sum()` for aggregations
- Use `case()` for conditional aggregation
- Use `ilike()` for case-insensitive search
- Use `order_by()` for sorting
- Use `offset()`/`limit()` for pagination

### 4. Relationships: ForeignKey and back_populates

```python
# models/relationships.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Parent(SQLModel, table=True):
    """Parent model linked to students"""
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    phone: Optional[str]

    # One-to-Many: Parent can have multiple students
    students: List["Student"] = Relationship(
        back_populates="parent",
        link_model="student_parent_link"  # Many-to-many through table
    )

class StudentParentLink(SQLModel, table=True):
    """Many-to-many link table for Student and Parent"""
    student_id: str = Field(foreign_key="student.id", primary_key=True)
    parent_id: str = Field(foreign_key="parent.id", primary_key=True)
    relationship_type: str = Field(default="father")  # father, mother, guardian

# Updated Student with many-to-many relationship
class Student(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)

    # Many-to-Many: Students can have multiple parents
    parents: List[Parent] = Relationship(
        back_populates="students",
        link_model=StudentParentLink
    )

# One-to-One relationship example
class StudentProfile(SQLModel, table=True):
    """One-to-one profile for student"""
    id: Optional[str] = Field(default=None, primary_key=True)
    student_id: str = Field(foreign_key="student.id", unique=True)
    bio: Optional[str] = None
    avatar_url: Optional[str]
    preferences: Optional[str] = None  # JSON string for flexible data

    student: Optional[Student] = Relationship()

# Self-referential relationship
class Employee(SQLModel, table=True):
    """Employee with manager relationship"""
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    manager_id: Optional[str] = Field(foreign_key="employee.id")

    # Self-referential relationship
    manager: Optional["Employee"] = Relationship(
        back_populates="subordinates",
        sa_relationship_kwargs={"remote_side": "[Employee.id]"}
    )
    subordinates: List["Employee"] = Relationship(back_populates="manager")
```

**Requirements:**
- Use `foreign_key` for relational links
- Use `back_populates` for bidirectional relationships
- Use `unique=True` for one-to-one relationships
- Use link tables for many-to-many relationships
- Use `remote_side` for self-referential relationships
- Use `sa_relationship_kwargs` for advanced SQLAlchemy options

## Output Requirements

### Code Files

1. **Models**:
   - `models/__init__.py`
   - `models/student.py`
   - `models/fee.py`
   - `models/attendance.py`
   - `models/class.py`

2. **CRUD Operations**:
   - `crud/__init__.py`
   - `crud/student.py`
   - `crud/fee.py`
   - `crud/attendance.py`

3. **Advanced Queries**:
   - `queries/__init__.py`
   - `queries/advanced.py`

### Integration Requirements

- **@fastapi-app**: Use models in FastAPI routes
- **@fastapi-app/dependencies**: DB session dependency
- **@api-client**: Type-safe responses for frontend

### Documentation

- **PHR**: Create Prompt History Record for schema design
- **ADR**: Document relationship choices, indexing strategy
- **Comments**: Document complex queries and relationships

## Workflow

1. **Design Schema**
   - Identify entities (Student, Fee, Attendance, etc.)
   - Define relationships (one-to-many, many-to-many)
   - Add constraints (unique, foreign keys, indexes)

2. **Create Models**
   - Define SQLModel classes with `table=True`
   - Add fields with types and validators
   - Configure relationships with `back_populates`

3. **Build CRUD Operations**
   - Implement create, read, update, delete
   - Add pagination and filtering
   - Handle async sessions

4. **Create Advanced Queries**
   - Implement joins and subqueries
   - Add aggregations and summaries
   - Search and filter functionality

5. **Test and Optimize**
   - Test all CRUD operations
   - Verify relationships work correctly
   - Optimize slow queries with indexes

## Quality Checklist

Before completing any SQLModel implementation:

- [ ] **Indexes on freq queries**: Add index=True for commonly filtered/sorted fields
- [ ] **Constraints FK/unique**: Use foreign_key for relations, unique=True for emails
- [ ] **Typed results**: Return properly typed Optional[T] or List[T]
- [ ] **Async support**: Use AsyncSession for all operations
- [ ] **Relationships**: Use back_populates for bidirectional links
- [ ] **Validation**: Use Field validators (min_length, max_length, pattern)
- [ ] **Timestamps**: Include created_at and updated_at
- [ ] **Cascading**: Configure delete behavior for relationships
- [ ] **Eager loading**: Use selectinload for relationship access
- [ ] **Error handling**: Handle IntegrityError, foreign key violations

## Common Patterns

### Student Model with CRUD

```python
# models/student.py
class Student(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=100, index=True)
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    fees: List["Fee"] = Relationship(back_populates="student")
```

### CRUD Fees

```python
# crud/fee.py
class FeeCRUD:
    @staticmethod
    async def create(db: AsyncSession, fee_data: FeeCreate) -> Fee:
        fee = Fee(**fee_data.model_dump())
        db.add(fee)
        await db.commit()
        await db.refresh(fee)
        return fee

    @staticmethod
    async def get_by_id(db: AsyncSession, fee_id: str) -> Optional[Fee]:
        result = await db.execute(
            select(Fee).where(Fee.id == fee_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_pending_by_student(db: AsyncSession, student_id: str) -> List[Fee]:
        result = await db.execute(
            select(Fee)
            .where(
                and_(
                    Fee.student_id == student_id,
                    Fee.status == "pending"
                )
            )
            .order_by(Fee.due_date)
        )
        return result.scalars().all()
```

### Query with Join

```python
# Get students with their class name using join
async def get_students_with_class(db: AsyncSession) -> List[dict]:
    result = await db.execute(
        select(
            Student.id,
            Student.name,
            Student.email,
            Class.name.label("class_name"),
        )
        .outerjoin(Class, Student.class_id == Class.id)
        .order_by(Student.name)
    )
    return [dict(row._mapping) for row in result]
```

## Database Setup

```python
# database.py
from sqlmodel import create_engine, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/erp_db"
)

# Async engine
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

## Migrations with Alembic

```python
# alembic/env.py
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_url
from alembic import context

# Import models for autogenerate
from models.student import Student
from models.fee import Fee
from models.attendance import Attendance

target_metadata = SQLModel.metadata

# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head
```

## References

- SQLModel Documentation: https://sqlmodel.tiangolo.com
- SQLAlchemy Relationships: https://docs.sqlalchemy.org/en/20/orm/relationships.html
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Pydantic Validation: https://docs.pydantic.dev/latest/usage/validators/
- Alembic Migrations: https://alembic.sqlalchemy.org/en/latest/
