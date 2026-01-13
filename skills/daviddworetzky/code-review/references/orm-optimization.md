# ORM Optimization Quick Reference

Common ORM anti-patterns and optimization techniques for SQLAlchemy (used in the Geist project).

## N+1 Query Problem

The most common ORM performance issue. Occurs when you load a collection of objects, then access related objects in a loop, triggering one query per item.

### ❌ N+1 Query Anti-Pattern

```python
# This triggers 1 + N queries (1 for users, N for each user's posts)
users = session.query(User).all()
for user in users:
    print(user.posts)  # Lazy load triggers a query for EACH user

# Example: 100 users = 101 queries total

# Another common pattern
users = session.query(User).filter(User.active == True).all()
for user in users:
    # Each of these triggers a separate query
    posts_count = len(user.posts)
    comments_count = len(user.comments)
    # Total: 1 + (N * 2) queries
```

### ✅ Eager Loading Solution

```python
# Use joinedload for one-to-many (LEFT OUTER JOIN)
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Already loaded, no additional query

# Total: 1 query (with JOIN)

# Use selectinload for better performance with large collections
from sqlalchemy.orm import selectinload

users = session.query(User).options(selectinload(User.posts)).all()
for user in users:
    print(user.posts)  # Already loaded

# Total: 2 queries (1 for users, 1 for all posts in one batch)

# Load multiple relationships
users = session.query(User).options(
    selectinload(User.posts),
    selectinload(User.comments),
    selectinload(User.profile)
).all()

# Total: 4 queries (1 for users, 3 for relationships)
# Much better than 1 + (N * 3) queries!
```

## Choosing the Right Loading Strategy

### joinedload vs selectinload

**Use `joinedload`:**
- For one-to-one relationships
- When you need to filter on the related table
- When the related collection is small

```python
# Good for one-to-one
user = session.query(User).options(joinedload(User.profile)).first()

# Good for filtering
users = session.query(User).join(User.posts).filter(
    Post.published == True
).options(joinedload(User.posts)).all()
```

**Use `selectinload`:**
- For one-to-many or many-to-many relationships
- When related collections could be large
- Generally more efficient for collections

```python
# Better for collections
users = session.query(User).options(selectinload(User.posts)).all()
```

### ❌ Avoid subqueryload (Deprecated)

```python
# Don't use this anymore
users = session.query(User).options(subqueryload(User.posts)).all()
```

## Queries in Loops

### ❌ Anti-Pattern

```python
# Query inside loop
post_ids = [1, 2, 3, 4, 5]
posts = []
for post_id in post_ids:
    post = session.query(Post).filter(Post.id == post_id).first()
    posts.append(post)
# Total: N queries

# Counting in loop
users = session.query(User).all()
for user in users:
    post_count = session.query(Post).filter(Post.user_id == user.id).count()
    print(f"{user.name} has {post_count} posts")
# Total: 1 + N queries
```

### ✅ Batch Operations

```python
# Single query with IN clause
post_ids = [1, 2, 3, 4, 5]
posts = session.query(Post).filter(Post.id.in_(post_ids)).all()
# Total: 1 query

# Use aggregation
from sqlalchemy import func
user_post_counts = session.query(
    User.id,
    User.name,
    func.count(Post.id).label('post_count')
).join(Post).group_by(User.id, User.name).all()

for user_id, name, post_count in user_post_counts:
    print(f"{name} has {post_count} posts")
# Total: 1 query
```

## Loading Unnecessary Data

### ❌ Loading Full Objects

```python
# Loading all columns when you only need a few
users = session.query(User).all()
for user in users:
    print(user.email)  # Only need email, but loaded entire user object

# Loading entire table
all_posts = session.query(Post).all()  # Could be millions of rows!
for post in all_posts:
    process(post)
```

### ✅ Load Only What You Need

```python
# Load specific columns
emails = session.query(User.email).all()
for (email,) in emails:
    print(email)

# Use pagination for large datasets
from sqlalchemy import desc

page = 1
page_size = 100
posts = session.query(Post).order_by(desc(Post.created_at)).limit(page_size).offset((page - 1) * page_size).all()

# Use defer() to skip loading large columns
from sqlalchemy.orm import defer

users = session.query(User).options(defer(User.profile_image)).all()
# profile_image column is not loaded unless explicitly accessed
```

## Missing Database Indexes

### ❌ Queries Without Indexes

```python
# SQLAlchemy model without indexes on foreign keys
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # No index!
    title = Column(String)
    content = Column(Text)
    created_at = Column(DateTime)

# Query will be slow
posts = session.query(Post).filter(Post.user_id == 123).all()
# Full table scan if user_id is not indexed!
```

### ✅ Add Indexes

```python
# Add index on foreign key
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)  # Indexed!
    title = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, index=True)  # Index on frequently queried columns

# Composite indexes for common query patterns
class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),  # Composite index
    )
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
```

## Inefficient Counting

### ❌ Loading All Rows to Count

```python
# Loading all objects just to count them
users = session.query(User).all()
count = len(users)  # Loaded all users into memory!

# Count with relationships
user = session.query(User).first()
post_count = len(user.posts)  # Loads all posts just to count
```

### ✅ Use count()

```python
# Efficient counting
count = session.query(User).count()  # SELECT COUNT(*)
# Or
from sqlalchemy import func
count = session.query(func.count(User.id)).scalar()

# Count relationships efficiently
from sqlalchemy import func
post_count = session.query(func.count(Post.id)).filter(Post.user_id == user.id).scalar()

# Or use column_property for frequently accessed counts
from sqlalchemy.orm import column_property
from sqlalchemy import select, func

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    post_count = column_property(
        select(func.count(Post.id)).where(Post.user_id == id).scalar_subquery()
    )
```

## Inefficient Existence Checks

### ❌ Loading Objects for Existence Check

```python
# Loading full object just to check existence
user = session.query(User).filter(User.email == email).first()
if user:
    print("User exists")

# Counting for existence
count = session.query(User).filter(User.email == email).count()
if count > 0:
    print("User exists")
```

### ✅ Use exists()

```python
from sqlalchemy import exists

# Efficient existence check
user_exists = session.query(
    exists().where(User.email == email)
).scalar()

if user_exists:
    print("User exists")

# Or use limit(1) if you need the object anyway
user = session.query(User).filter(User.email == email).limit(1).first()
```

## Transaction and Flushing Issues

### ❌ Auto-flushing in Loops

```python
# Auto-flush triggers on every query in loop
for data in large_dataset:
    user = User(**data)
    session.add(user)
    # Implicit flush may occur on query operations
    existing = session.query(User).filter(User.email == data['email']).first()
```

### ✅ Bulk Operations

```python
# Bulk insert (bypasses ORM, very fast)
session.bulk_insert_mappings(User, large_dataset)

# Disable auto-flush in critical sections
with session.no_autoflush:
    for data in large_dataset:
        user = User(**data)
        session.add(user)
        existing = session.query(User).filter(User.email == data['email']).first()

# Single flush at the end
session.flush()
```

## Lazy vs Eager Defaults

### ❌ Wrong Lazy Loading Setting

```python
# Default lazy='select' causes N+1
class User(Base):
    __tablename__ = 'users'
    posts = relationship('Post', back_populates='user')  # default lazy='select'

# Always triggers N+1 if you iterate
users = session.query(User).all()
for user in users:
    print(user.posts)  # N+1 queries
```

### ✅ Choose Appropriate Default

```python
# Set lazy='selectin' as default for collections often accessed together
class User(Base):
    __tablename__ = 'users'
    posts = relationship('Post', back_populates='user', lazy='selectin')

# Now automatically uses efficient loading
users = session.query(User).all()
for user in users:
    print(user.posts)  # Only 2 queries total

# Or use lazy='joined' for one-to-one relationships
class User(Base):
    __tablename__ = 'users'
    profile = relationship('Profile', back_populates='user', lazy='joined', uselist=False)
```

## Code Review Checklist for ORM

When reviewing SQLAlchemy code, check for:

- [ ] **N+1 Queries**: Look for relationship access in loops without eager loading
- [ ] **Missing Eager Loading**: Check if `joinedload()` or `selectinload()` is used when needed
- [ ] **Queries in Loops**: Ensure batch operations are used instead
- [ ] **Missing Indexes**: Verify foreign keys and frequently queried columns are indexed
- [ ] **Loading Full Objects**: Check if only specific columns could be loaded instead
- [ ] **Inefficient Counting**: Verify `count()` is used instead of `len(query.all())`
- [ ] **Inefficient Existence Checks**: Verify `exists()` is used instead of loading full objects
- [ ] **Large Result Sets**: Check for pagination or streaming for large queries
- [ ] **Bulk Operations**: Verify bulk operations are used for large inserts/updates
- [ ] **Transaction Management**: Check for proper transaction boundaries and commits

## Performance Testing

```python
# Add logging to see SQL queries
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Count queries in a test
from sqlalchemy import event

query_count = 0

def count_queries(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1

event.listen(engine, "before_cursor_execute", count_queries)

# Run your code
users = session.query(User).all()
for user in users:
    print(user.posts)

print(f"Total queries: {query_count}")
# If this is > 2 for a simple loop, you have an N+1 problem
```

## Common Red Flags in Code Review

Look for these patterns that indicate performance issues:

```python
# RED FLAG: Accessing relationships in loops without eager loading
for user in users:
    user.posts  # Lazy load

# RED FLAG: Query inside loop
for id in ids:
    obj = session.query(Model).get(id)

# RED FLAG: Loading all to count
count = len(session.query(Model).all())

# RED FLAG: Multiple separate queries that could be joined
users = session.query(User).all()
posts = session.query(Post).all()
# Better: join them if they're related

# RED FLAG: No indexes on foreign keys
user_id = Column(Integer, ForeignKey('users.id'))  # Missing index=True

# RED FLAG: Loading large columns unnecessarily
users = session.query(User).all()  # Loads all columns including large ones
```
