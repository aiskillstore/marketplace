# FastAPI Intermediate Guide

This guide covers authentication, database integration, dependency injection, middleware, and advanced request handling.

## Table of Contents

- [Authentication & Authorization](#authentication--authorization)
- [Database Integration](#database-integration)
- [Dependency Injection](#dependency-injection)
- [Middleware & CORS](#middleware--cors)
- [Background Tasks](#background-tasks)
- [File Operations](#file-operations)

## Authentication & Authorization

### JWT Authentication

**Install dependencies:**
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

**Token schema and utilities:**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "your-secret-key-here"  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**User authentication:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
```

### Role-Based Access Control

```python
from enum import Enum
from typing import List

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class UserInDB(User):
    hashed_password: str
    roles: List[Role] = []

def require_roles(allowed_roles: List[Role]):
    async def role_checker(current_user: UserInDB = Depends(get_current_active_user)):
        if not any(role in current_user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserInDB = Depends(require_roles([Role.ADMIN]))
):
    return {"message": f"User {user_id} deleted by {current_user.username}"}
```

## Database Integration

### SQLAlchemy Setup

**Install dependencies:**
```bash
pip install sqlalchemy databases[postgresql]
```

**Database configuration:**
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# For SQLite: "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**Database models:**
```python
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class DBItem(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    is_available = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("DBUser", back_populates="items")

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("DBItem", back_populates="owner")

# Create tables
Base.metadata.create_all(bind=engine)
```

**Database dependency:**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**CRUD operations:**
```python
from sqlalchemy.orm import Session
from fastapi import Depends

@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = DBItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/items/", response_model=List[ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(DBItem).offset(skip).limit(limit).all()
    return items

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}
```

### Async Database (Databases library)

```python
import databases
from sqlalchemy import MetaData

DATABASE_URL = "postgresql://user:password@localhost/dbname"
database = databases.Database(DATABASE_URL)
metadata = MetaData()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/items/")
async def read_items():
    query = "SELECT * FROM items"
    results = await database.fetch_all(query)
    return results

@app.post("/items/")
async def create_item(item: ItemCreate):
    query = "INSERT INTO items(name, description, price) VALUES (:name, :description, :price)"
    values = {"name": item.name, "description": item.description, "price": item.price}
    last_record_id = await database.execute(query=query, values=values)
    return {**item.dict(), "id": last_record_id}
```

## Dependency Injection

### Basic Dependencies

```python
from typing import Optional

async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons
```

### Class-Based Dependencies

```python
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends()):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

### Sub-Dependencies

```python
def query_extractor(q: Optional[str] = None):
    return q

def query_or_cookie_extractor(
    q: str = Depends(query_extractor),
    last_query: Optional[str] = Cookie(None)
):
    if not q:
        return last_query
    return q

@app.get("/items/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}
```

### Dependencies with Yield

```python
async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        await db.close()

@app.get("/items/")
async def read_items(db: DBSession = Depends(get_db)):
    items = await db.fetch_all("SELECT * FROM items")
    return items
```

## Middleware & CORS

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://example.com"],  # Specific origins
    # allow_origins=["*"],  # Allow all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
```

### Custom Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Request Logging Middleware

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response
```

### Rate Limiting Middleware

```python
from collections import defaultdict
from datetime import datetime, timedelta

# Simple in-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    now = datetime.now()

    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if now - req_time < timedelta(minutes=1)
    ]

    if len(request_counts[client_ip]) >= 100:  # 100 requests per minute
        raise HTTPException(status_code=429, detail="Too many requests")

    request_counts[client_ip].append(now)
    response = await call_next(request)
    return response
```

## Background Tasks

### Basic Background Tasks

```python
from fastapi import BackgroundTasks

def write_notification(email: str, message: str):
    with open("log.txt", mode="a") as log:
        log.write(f"Notification to {email}: {message}\n")

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks,
    message: str = "Default message"
):
    background_tasks.add_task(write_notification, email, message)
    return {"message": "Notification sent in the background"}
```

### Multiple Background Tasks

```python
def send_email(email: str, subject: str, body: str):
    # Simulate sending email
    time.sleep(2)
    print(f"Email sent to {email}")

def update_database(user_id: int):
    # Simulate database update
    time.sleep(1)
    print(f"Database updated for user {user_id}")

@app.post("/register/")
async def register_user(
    email: str,
    user_id: int,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome", "Thanks for registering!")
    background_tasks.add_task(update_database, user_id)
    return {"message": "User registered"}
```

## File Operations

### File Upload

```python
from fastapi import File, UploadFile
from typing import List
import shutil

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "content_type": file.content_type}

@app.post("/upload-multiple/")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    filenames = []
    for file in files:
        with open(f"uploads/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
    return {"filenames": filenames}
```

### File Upload with Size Limit

```python
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

### File Download

```python
from fastapi.responses import FileResponse
import os

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"uploads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
```

### Streaming File Response

```python
from fastapi.responses import StreamingResponse
import io

@app.get("/stream-csv/")
async def stream_csv():
    def generate_csv():
        yield "id,name,value\n"
        for i in range(1000):
            yield f"{i},Item {i},{i * 10}\n"

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data.csv"}
    )
```

## Configuration Management

### Using Environment Variables

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    admin_email: str
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

@app.get("/info")
async def info():
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email
    }
```

**.env file:**
```
APP_NAME=My FastAPI Application
ADMIN_EMAIL=admin@example.com
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
```

## Next Steps

For advanced topics, see **references/03-advanced.md** covering WebSockets, testing, deployment, and performance optimization.
