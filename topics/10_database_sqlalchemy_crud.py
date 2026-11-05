"""
Topic 10: Database Integration with SQLAlchemy ORM (CRUD & Transactions)
========================================================================
(Reference: Pages 14, 15, and 16 of the Notes)

Key Concepts Explained:
-----------------------
1. SQLAlchemy ORM:
   - Object-Relational Mapper that maps Python classes to database tables.
   - We define database models using `Base = declarative_base()` or `DeclarativeBase`.

2. The Database Session Dependency (`get_db`):
   - In FastAPI, every HTTP request receives its own isolated database session via `Depends(get_db)`.
   - Pattern:
     ```python
     def get_db():
         db = SessionLocal()
         try:
             yield db          # Injected into the endpoint
         finally:
             db.close()        # Always closed when the request finishes!
     ```

3. Transactions & Rollback:
   - Multiple operations can be grouped into one atomic transaction.
   - If an error occurs, `db.rollback()` ensures database integrity is preserved.

How to Run This Demo:
---------------------
Run in terminal:
    uv run python topics/10_database_sqlalchemy_crud.py

Then visit:
    http://127.0.0.1:8000/docs
"""

from typing import Generator
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ===================================================================
# 1. Database Configuration (Using SQLite for instant zero-config setup)
# ===================================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_learning.db"

# connect_args={"check_same_thread": False} is required only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True if you want to see raw SQL queries in console!
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ===================================================================
# 2. SQLAlchemy Database Model
# ===================================================================
class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)


# Create all tables on startup
Base.metadata.create_all(bind=engine)


# ===================================================================
# 3. Pydantic Schemas for Validation
# ===================================================================
class ItemCreate(BaseModel):
    title: str
    description: str | None = None
    price: int
    is_available: bool = True


class ItemResponse(ItemCreate):
    id: int

    class Config:
        from_attributes = True


# ===================================================================
# 4. Database Session Dependency
# ===================================================================
def get_db() -> Generator[Session, None, None]:
    """Provides a transactional database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================================================================
# 5. FastAPI Application & CRUD Endpoints
# ===================================================================
app = FastAPI(
    title="Topic 10: SQLAlchemy Database Integration",
    description="Learn SessionLocal, get_db dependency, CRUD operations, and transaction handling.",
    version="1.0.0",
)


# CREATE
@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, tags=["CRUD"])
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Creates a new record in the database."""
    db_item = ItemDB(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# READ ALL
@app.get("/items", response_model=list[ItemResponse], tags=["CRUD"])
def read_items(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Fetches a list of records with pagination."""
    return db.query(ItemDB).offset(skip).limit(limit).all()


# READ ONE
@app.get("/items/{item_id}", response_model=ItemResponse, tags=["CRUD"])
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Fetches a single record by primary key."""
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return db_item


# UPDATE
@app.put("/items/{item_id}", response_model=ItemResponse, tags=["CRUD"])
def update_item(item_id: int, updated: ItemCreate, db: Session = Depends(get_db)):
    """Updates an existing record."""
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    for key, value in updated.model_dump().items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


# DELETE
@app.delete("/items/{item_id}", tags=["CRUD"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Deletes a record."""
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    db.delete(db_item)
    db.commit()
    return {"status": "success", "message": f"Item {item_id} deleted"}


# TRANSACTION & ROLLBACK DEMO
@app.post("/demo/transaction-rollback", tags=["Transactions"])
def demo_transaction(should_fail: bool = True, db: Session = Depends(get_db)):
    """
    Demonstrates atomic transaction handling:
    If an unexpected error occurs halfway through, rollback() restores the clean state.
    """
    try:
        new_item = ItemDB(title="Temp Item", price=100)
        db.add(new_item)
        db.flush()  # Assigns ID without permanently committing yet

        if should_fail:
            raise ValueError("Simulated unexpected crash during payment processing!")

        db.commit()
        return {"status": "committed", "item_id": new_item.id}
    except Exception as e:
        db.rollback()  # Undo any changes!
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction rolled back due to error: {str(e)}",
        )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Topic 10: Database Integration Demo Starting!")
    print("👉 Database file created: ./fastapi_learning.db")
    print("👉 Test CRUD and Transactions in Swagger UI:")
    print("   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("10_database_sqlalchemy_crud:app", host="127.0.0.1", port=8000, reload=True)
