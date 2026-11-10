
import os
from decimal import Decimal

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)

router = APIRouter()

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://127.0.0.1:8001"
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    # Step 1: Verify product with Product Service
    try:
        response = httpx.get(
            f"{PRODUCT_SERVICE_URL}/products/{order_data.product_id}",
            timeout=5.0
        )
        response.raise_for_status()
        product = response.json()

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        raise HTTPException(
            status_code=502,
            detail="Product Service returned an error"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Product Service is unavailable"
        )

    # Step 2: Calculate order amount
    unit_price = Decimal(str(product["price"]))
    total_amount = unit_price * order_data.quantity

    # Step 3: Create order
    new_order = Order(
        customer_id=order_data.customer_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        status="PLACED"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id.desc()).all()


@router.get("/customer/{customer_id}", response_model=list[OrderResponse])
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Order).filter(
        Order.customer_id == customer_id
    ).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    order.status = status_data.status
    db.commit()
    db.refresh(order)

    return order
