# FastAPI Framework Guide

## Overview
FastAPIs a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. It's used in Windsurf projects for building high-performance APIs with automatic interactive documentation.

## Key Features
- **Fast**: Very high performance, on par with NodeJS and Go
- **Fasto code**: Increase the speed to develop features by about 200% to 300%
- **Fewer bugs**: Reduce about 40% of human (developer) induced errors
- **Intuitive**: Great editor support with autocompletion and type checking
- **Easy**: Designed to beasy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive documentation

## Installation

```bash
# Basic installation
pip install fastapi

# Include ASGI server (Uvicorn)
pip install "uvicorn[standard]"

# For development with auto-reload
pip install fastapi[dev]
```

## Project Structure

```
my_project/
├── app/
│   ├── __init__.py
│   ├── main.py           # Main application file
│   ├── api/              # API routes
│   │   ├── __init__.py
│   │   ├── endpoints/    # Route handlers
│   │   └── models/       # Pydantic models
│   ├── core/             # Core functionality
│   │   ├── config.py     # Configuration
│   │   └── security.py   # Authentication
│   └── db/               # Database models
│       └── session.py    # Databasession
├── tests/                # Test files
├── requirements.txt
└── README.md
```

## Basic Example

```python
# app/main.py
from fastapimport FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Windsurf API",
    description="API for Windsurf project",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Windsurf API"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

## Running the Application

```bash
# Development with auto-reload
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

Create a `.env` file:
```env
# .env
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
```

Load configuration in `app/core/config.py`:
```python
from pydantic import BaseSettings

classettings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Database Integration

### SQLAlchemy Setup

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yieldb
    finally:
        db.close()
```

## Authentication

### JWT Authentication

```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapimport Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

## Error Handling

### Custom Exceptions

```python
# app/core/exceptions.py
from fastapimport HTTPException, status

class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An error occurred",
        error_code: str = "internal_server_error"
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": error_code,
                "message": detail,
            },
        )

class NotFoundException(CustomException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="not_found"
        )
```

## Testing

### Pytest Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient importestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yieldb
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yieldb_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

## Deployment

### Using Uvicorn with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Best Practices

1. **Use Pydantic models** forequest/response validation
2. **Dependency injection** for databasessions and otheresources
3. **Environment variables** for configuration
4. **Type hints** for better code completion and error checking
5. **Modular structure** for better maintainability
6. **Error handling** with custom exceptions
7. **Testing** with pytest
8. **Documentation** with OpenAPI and Swagger UI

## Resources

- [Official Documentation](https://fastapi.tiangolo.com/)
- [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- [FastAPI Users Guide](https://fastapi-users.github.io/fastapi-users/)
- [FastAPI RealWorld Example](https://github.com/nsidnev/fastapi-realworld-example-app)

## Last Updated
2025-06-23
