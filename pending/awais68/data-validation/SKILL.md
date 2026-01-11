---
name: data-validation
description: |
  Use when implementing data validation for API payloads, form inputs, or database writes.
  Triggers for: Pydantic models, Zod schemas, input sanitization, type validation,
  field constraints, or request/response schemas.
  NOT for: business logic (use domain services) or authentication/authorization.
---

# Data Validation Skill

Expert data validation for Python backends (Pydantic) and TypeScript frontends (Zod) with type-safe validation pipelines.

## Quick Reference

| Layer | Tool | Purpose |
|-------|------|---------|
| Backend | Pydantic v2 | Request/response validation |
| Frontend | Zod | Form validation, schema inference |
| Sanitization | bleach, strip-html | Input cleaning |
| Types | mypy, TypeScript | Compile-time safety |

## Project Structure

```
backend/
├── app/
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── student.py      # StudentCreate, StudentUpdate, StudentOut
│   │   ├── fee.py          # FeeCreate, FeeOut
│   │   └── common.py       # PaginationParams, ErrorDetail
│   └── models/             # SQLModel (separate from schemas)
frontend/
├── lib/
│   ├── schemas/
│   │   ├── student.schema.ts
│   │   └── index.ts        # Export all schemas
│   └── validation.ts       # Shared validation utilities
└── types/
    └── shared.ts           # Inferred types from Zod
```

## Backend: Pydantic Models

### Separate In/Out Models

```python
# backend/app/schemas/student.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# === CREATE Models (Input) ===

class StudentCreate(BaseModel):
    """Payload for creating a new student."""

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["John"],
        description="Student's first name",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Doe"],
    )
    email: EmailStr = Field(..., examples=["john.doe@school.edu"])
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+?[1-9]\d{9,14}$",
        examples=["+1234567890"],
    )
    date_of_birth: datetime = Field(..., description="Student's birth date")
    grade_level: int = Field(..., ge=1, le=12, examples=[9])
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@school.edu",
                    "date_of_birth": "2008-05-15T00:00:00Z",
                    "grade_level": 9,
                }
            ]
        }
    )


class StudentUpdate(BaseModel):
    """Payload for updating a student. All fields optional."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{9,14}$")
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    is_active: Optional[bool] = None


# === OUTPUT Models (Response) ===

class StudentOut(BaseModel):
    """Response model for student data."""

    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: datetime
    grade_level: int
    enrollment_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentWithFees(StudentOut):
    """Student with nested fee information."""

    fees: list["FeeOut"] = []
```

### Custom Validators

```python
# backend/app/schemas/student.py (continued)
from pydantic import field_validator, model_validator
from datetime import date


class StudentCreate(BaseModel):
    # ... fields as above

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def parse_date_of_birth(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @model_validator(mode="after")
    def validate_age_range(self):
        """Ensure student is a reasonable age for school."""
        dob = self.date_of_birth
        if isinstance(dob, datetime):
            dob = dob.date()

        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 5:
            raise ValueError("Student must be at least 5 years old")
        if age > 25:
            raise ValueError("Age seems unreasonable for school enrollment")
        return self
```

### Common Schemas

```python
# backend/app/schemas/common.py
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Max records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""

    data: List[T]
    total: int = Field(..., description="Total count of records")
    skip: int
    limit: int
    has_more: bool = Field(..., description="Whether more records exist")


class ErrorDetail(BaseModel):
    """Detailed validation error."""

    field: str = Field(..., examples=["email"])
    message: str = Field(..., examples=["Invalid email format"])
    code: str = Field(..., examples=["value_error"])


class ValidationErrorResponse(BaseModel):
    """Standard validation error response."""

    error: dict = Field(..., description="Error details")
    details: Optional[List[ErrorDetail]] = None


# === Search & Filter ===

class SearchParams(BaseModel):
    """Standard search parameters."""

    query: Optional[str] = Field(None, min_length=1, max_length=200)
    sort_by: str = Field("created_at")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
```

## Frontend: Zod Schemas

### Basic Schemas

```typescript
// frontend/lib/schemas/student.schema.ts
import { z } from "zod";

// === CONSTANTS (shared with backend) ===
const NAME_MIN_LENGTH = 1;
const NAME_MAX_LENGTH = 100;
const PHONE_REGEX = /^\+?[1-9]\d{9,14}$/;
const GRADE_MIN = 1;
const GRADE_MAX = 12;

// === CREATE SCHEMA ===
export const studentCreateSchema = z.object({
  first_name: z
    .string()
    .min(NAME_MIN_LENGTH, { message: "First name is required" })
    .max(NAME_MAX_LENGTH, { message: "Maximum 100 characters allowed" })
    .trim(),

  last_name: z
    .string()
    .min(NAME_MIN_LENGTH, { message: "Last name is required" })
    .max(NAME_MAX_LENGTH, { message: "Maximum 100 characters allowed" })
    .trim(),

  email: z.string().email({ message: "Invalid email address" }),

  phone: z
    .string()
    .regex(PHONE_REGEX, { message: "Invalid phone number format" })
    .optional()
    .or(z.literal("")),

  date_of_birth: z.string().datetime({ message: "Invalid date format" }),

  grade_level: z
    .number()
    .int()
    .min(GRADE_MIN, { message: `Grade must be at least ${GRADE_MIN}` })
    .max(GRADE_MAX, { message: `Grade cannot exceed ${GRADE_MAX}` }),
});

// === UPDATE SCHEMA (partial) ===
export const studentUpdateSchema = studentCreateSchema.partial();

// === OUTPUT/RESPONSE SCHEMA ===
export const studentOutSchema = z.object({
  id: z.number(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string().email(),
  phone: z.string().nullable(),
  date_of_birth: z.string().datetime(),
  grade_level: z.number().int().min(GRADE_MIN).max(GRADE_MAX),
  enrollment_date: z.string().datetime(),
  is_active: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

// === INFERRED TYPES ===
export type StudentCreateInput = z.infer<typeof studentCreateSchema>;
export type StudentUpdateInput = z.infer<typeof studentUpdateSchema>;
export type StudentOutput = z.infer<typeof studentOutSchema>;
```

### Advanced Zod Patterns

```typescript
// frontend/lib/schemas/student.schema.ts (continued)
import { date, string } from "zod";

// === CROSS-FIELD VALIDATION ===
export const studentCreateSchema = z
  .object({
    first_name: z.string().min(1).max(100),
    last_name: z.string().min(1).max(100),
    email: z.string().email(),
    phone: z.string().regex(/^\+?[1-9]\d{9,14}$/).optional(),
    date_of_birth: z.string().datetime(),
    grade_level: z.number().int().min(1).max(12),
  })
  .refine(
    (data) => {
      // Cross-field validation: date of birth must be in the past
      const dob = new Date(data.date_of_birth);
      return dob < new Date();
    },
    {
      message: "Date of birth must be in the past",
      path: ["date_of_birth"],
    }
  )
  .refine(
    (data) => {
      // Ensure age is reasonable for school
      const dob = new Date(data.date_of_birth);
      const age =
        new Date().getFullYear() - dob.getFullYear();
      return age >= 5 && age <= 25;
    },
    {
      message: "Student age must be between 5 and 25 years",
      path: ["date_of_birth"],
    }
  );

// === CUSTOM TRANSFORMERS ===
export const phoneSchema = z
  .string()
  .regex(/^\+?[1-9]\d{9,14}$/, { message: "Invalid phone number" })
  .transform((phone) => phone.replace(/\s+/g, "")); // Normalize

// === ENUM SCHEMAS ===
export const feeStatusSchema = z.enum(["pending", "paid", "overdue", "waived"]);

// === NESTED SCHEMAS ===
export const addressSchema = z.object({
  street: z.string().min(1).max(200),
  city: z.string().min(1).max(100),
  state: z.string().min(2).max(50),
  zip_code: z.string().regex(/^\d{5}(-\d{4})?$/),
  country: z.string().min(2).max(100).default("USA"),
});

export const studentWithAddressSchema = studentOutSchema.extend({
  address: addressSchema.nullable(),
});

// === DISCRIMINATED UNIONS ===
export const enrollmentStatusSchema = z.discriminatedUnion("status", [
  z.object({
    status: z.literal("active"),
    last_attendance_date: z.string().datetime(),
  }),
  z.object({
    status: z.literal("inactive"),
    reason: z.string().min(1),
    inactive_since: z.string().datetime(),
  }),
  z.object({
    status: z.literal("pending"),
    expected_start_date: z.string().datetime(),
  }),
]);
```

### Form Integration

```typescript
// frontend/components/StudentForm.tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { studentCreateSchema, type StudentCreateInput } from "@/lib/schemas/student.schema";

export function StudentForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<StudentCreateInput>({
    resolver: zodResolver(studentCreateSchema),
    mode: "onBlur",
  });

  const onSubmit = async (data: StudentCreateInput) => {
    try {
      const response = await fetch("/api/v1/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();

        // Map backend errors to form fields
        if (errorData.details) {
          for (const detail of errorData.details) {
            setError(detail.field as keyof StudentCreateInput, {
              message: detail.message,
            });
          }
        }
        return;
      }

      // Success handling
      router.push("/students");
    } catch {
      // Network or unexpected error
      setError("root", {
        message: "An unexpected error occurred. Please try again.",
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* First Name */}
      <div>
        <label htmlFor="first_name">First Name</label>
        <input
          id="first_name"
          {...register("first_name")}
          className={errors.first_name ? "border-red-500" : ""}
        />
        {errors.first_name && (
          <p className="text-red-500">{errors.first_name.message}</p>
        )}
      </div>

      {/* Last Name */}
      <div>
        <label htmlFor="last_name">Last Name</label>
        <input
          id="last_name"
          {...register("last_name")}
          className={errors.last_name ? "border-red-500" : ""}
        />
        {errors.last_name && (
          <p className="text-red-500">{errors.last_name.message}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register("email")}
          className={errors.email ? "border-red-500" : ""}
        />
        {errors.email && (
          <p className="text-red-500">{errors.email.message}</p>
        )}
      </div>

      {/* Grade Level */}
      <div>
        <label htmlFor="grade_level">Grade Level</label>
        <select
          id="grade_level"
          {...register("grade_level", { valueAsNumber: true })}
          className={errors.grade_level ? "border-red-500" : ""}
        >
          {Array.from({ length: 12 }, (_, i) => i + 1).map((grade) => (
            <option key={grade} value={grade}>
              Grade {grade}
            </option>
          ))}
        </select>
        {errors.grade_level && (
          <p className="text-red-500">{errors.grade_level.message}</p>
        )}
      </div>

      {/* Date of Birth */}
      <div>
        <label htmlFor="date_of_birth">Date of Birth</label>
        <input
          id="date_of_birth"
          type="date"
          {...register("date_of_birth")}
          className={errors.date_of_birth ? "border-red-500" : ""}
        />
        {errors.date_of_birth && (
          <p className="text-red-500">{errors.date_of_birth.message}</p>
        )}
      </div>

      {errors.root && (
        <p className="text-red-500">{errors.root.message}</p>
      )}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create Student"}
      </button>
    </form>
  );
}
```

## Input Sanitization

### Backend Sanitization

```python
# backend/app/core/sanitize.py
import re
from typing import Any


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return text
    # Simple strip - use bleach for more robust sanitization
    return re.sub(r"<[^>]*>", "", text)


def sanitize_string(
    value: Any,
    max_length: int = None,
    allow_html: bool = False,
) -> str:
    """Sanitize a string value."""
    if value is None:
        return ""

    s = str(value).strip()

    if not allow_html:
        s = strip_html(s)

    if max_length:
        s = s[:max_length]

    return s


def sanitize_for_database(value: Any) -> Any:
    """General database input sanitization."""
    if isinstance(value, str):
        return sanitize_string(value, max_length=10000)
    if isinstance(value, list):
        return [sanitize_for_database(v) for v in value]
    if isinstance(value, dict):
        return {k: sanitize_for_database(v) for k, v in value.items()}
    return value
```

### Validator with Sanitization

```python
# backend/app/schemas/student.py
from pydantic import field_validator


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def sanitize_names(cls, v):
        if isinstance(v, str):
            return sanitize_string(v, max_length=100)
        return v
```

## Schema Sharing Strategy

### Field Consistency

```python
# backend/app/schemas/student.py
class StudentCreate(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        json_schema_extra={
            "frontend_type": "text",
            "validation": {
                "min": 1,
                "max": 100,
            },
        },
    )
```

```typescript
// frontend/lib/schemas/shared/constants.ts
// Match backend constraints
export const STUDENT_NAME_MAX_LENGTH = 100;
export const STUDENT_NAME_MIN_LENGTH = 1;
export const PHONE_REGEX = /^\+?[1-9]\d{9,14}$/;
export const GRADE_MIN = 1;
export const GRADE_MAX = 12;
```

### Contract Documentation

```markdown
# Student Schema Contract

## StudentCreate

| Field | Type | Required | Min | Max | Pattern | Description |
|-------|------|----------|-----|-----|---------|-------------|
| first_name | string | yes | 1 | 100 | - | Student's first name |
| last_name | string | yes | 1 | 100 | - | Student's last name |
| email | string (email) | yes | - | - | RFC 5322 | Valid email address |
| phone | string | no | - | 15 | `^\+?[1-9]\d{9,14}$` | E.164 format |
| date_of_birth | datetime | yes | - | - | ISO 8601 | Birth date |
| grade_level | int | yes | 1 | 12 | - | Grade (K-12) |
```

## Quality Checklist

- [ ] **All external inputs validated**: Every API input has a schema
- [ ] **Helpful error messages**: Each field has clear, actionable validation messages
- [ ] **No trust on client-only validation**: Backend re-validates all inputs
- [ ] **Length/format constraints defined**: All string fields have min/max
- [ ] **Separate in/out models**: Create/Update (input) vs Output (response)
- [ ] **Type-safe pipeline**: Frontend Zod infers TypeScript types
- [ ] **Sanitization applied**: Input cleaning before validation

## Integration Points

| Skill | Integration |
|-------|-------------|
| `@api-route-design` | Use schemas in `response_model`, `Body()` |
| `@error-handling` | Validation errors return proper error codes |
| `@fastapi-app` | Auto-generated OpenAPI docs from Pydantic |
| `@sqlmodel-crud` | Create/Update schemas match model fields |
