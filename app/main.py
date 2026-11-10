
from fastapi import FastAPI

from app.database import Base, engine
from app.models.order import Order
from app.routes import orders

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShopSphere Order Service",
    description="Microservice responsible for order management",
    version="1.0.0"
)

# Register order routes
app.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders"]
)


@app.get("/")
def root():
    return {
        "message": "Welcome to ShopSphere Order Service"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "order-service"
    }
