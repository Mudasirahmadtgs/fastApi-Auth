from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth_routes

app = FastAPI()

# Create all tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(auth_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Authentication System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)