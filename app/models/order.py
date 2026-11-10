from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    customer_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )

    product_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="PLACED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )