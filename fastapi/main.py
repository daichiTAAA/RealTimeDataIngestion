from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from datetime import datetime
from decimal import Decimal

# PostgreSQL Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/testdb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQL Server Database configuration
SQLSERVER_URL = os.getenv(
    "SQLSERVER_URL", "mssql+pymssql://sa:SqlServer123!@sqlserver:1433/testdb"
)

sqlserver_engine = create_engine(SQLSERVER_URL)
SqlServerSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlserver_engine)
SqlServerBase = declarative_base()


# Database models - PostgreSQL
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


# Database models - SQL Server
class SqlServerUser(SqlServerBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("GETDATE()"))
    updated_at = Column(TIMESTAMP, server_default=text("GETDATE()"))


class SqlServerProduct(SqlServerBase):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("GETDATE()"))
    updated_at = Column(TIMESTAMP, server_default=text("GETDATE()"))


# Pydantic models
class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    price: Decimal
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(title="Real-Time Data Ingestion API", version="1.0.0")


# Create tables on startup
@app.on_event("startup")
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("PostgreSQL tables created successfully")
    except Exception as e:
        print(f"Failed to create PostgreSQL tables: {e}")
    
    # Note: SQL Server tables are created via initialization script


# Dependencies to get database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sqlserver_db():
    db = SqlServerSessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Real-Time Data Ingestion API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# User endpoints
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# Product endpoints
@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


# SQL Server User endpoints
@app.post("/sqlserver/users/", response_model=UserResponse)
def create_sqlserver_user(user: UserCreate, db: Session = Depends(get_sqlserver_db)):
    db_user = SqlServerUser(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/sqlserver/users/", response_model=List[UserResponse])
def read_sqlserver_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_sqlserver_db)):
    users = db.query(SqlServerUser).offset(skip).limit(limit).all()
    return users


@app.get("/sqlserver/users/{user_id}", response_model=UserResponse)
def read_sqlserver_user(user_id: int, db: Session = Depends(get_sqlserver_db)):
    user = db.query(SqlServerUser).filter(SqlServerUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/sqlserver/users/{user_id}", response_model=UserResponse)
def update_sqlserver_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_sqlserver_db)):
    user = db.query(SqlServerUser).filter(SqlServerUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@app.delete("/sqlserver/users/{user_id}")
def delete_sqlserver_user(user_id: int, db: Session = Depends(get_sqlserver_db)):
    user = db.query(SqlServerUser).filter(SqlServerUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# SQL Server Product endpoints
@app.post("/sqlserver/products/", response_model=ProductResponse)
def create_sqlserver_product(product: ProductCreate, db: Session = Depends(get_sqlserver_db)):
    db_product = SqlServerProduct(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/sqlserver/products/", response_model=List[ProductResponse])
def read_sqlserver_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_sqlserver_db)):
    products = db.query(SqlServerProduct).offset(skip).limit(limit).all()
    return products


@app.get("/sqlserver/products/{product_id}", response_model=ProductResponse)
def read_sqlserver_product(product_id: int, db: Session = Depends(get_sqlserver_db)):
    product = db.query(SqlServerProduct).filter(SqlServerProduct.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/sqlserver/products/{product_id}", response_model=ProductResponse)
def update_sqlserver_product(
    product_id: int, product_update: ProductUpdate, db: Session = Depends(get_sqlserver_db)
):
    product = db.query(SqlServerProduct).filter(SqlServerProduct.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@app.delete("/sqlserver/products/{product_id}")
def delete_sqlserver_product(product_id: int, db: Session = Depends(get_sqlserver_db)):
    product = db.query(SqlServerProduct).filter(SqlServerProduct.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
