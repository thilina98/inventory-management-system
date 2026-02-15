from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Thilina!"}

@app.get("/logistics")
def read_logistics():
    return {"message": "Welcome to the Logistics Service!"}

# To run this app, use the command: uvicorn src.logistics.main:app --reload