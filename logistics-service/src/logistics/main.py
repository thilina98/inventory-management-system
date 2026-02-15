from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends
from sqlalchemy.exc import OperationalError
import os
from sqlalchemy.sql import text

# Read database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/logistics_db")
print(f"Using database URL: {DATABASE_URL}")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        print("+++++++++++++++++++")
        try:
          yield db
        except OperationalError as e:
            print('-------------------')
            print(f"Database connection error: {str(e)}")
            raise e
    finally:
        db.close()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Thilina!"}

@app.get("/logistics")
def read_logistics():
    return {"message": "Welcome to the Logistics Service!"}

@app.get("/test-db")
def test_db_connection(db: SessionLocal = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {"message": "Database connection successful!"}
    except OperationalError as e:
        return {"message": f"Database connection failed! Error: {str(e)}"}

# To run this app, use the command: uvicorn src.logistics.main:app --reload


