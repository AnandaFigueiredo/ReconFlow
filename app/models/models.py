from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database import Base


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)

    batch_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING"
    )

    total_a = Column(Integer, default=0)
    total_b = Column(Integer, default=0)
    total_matched = Column(Integer, default=0)
    total_divergent = Column(Integer, default=0)
    total_missing = Column(Integer, default=0)


class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(
        Integer,
        ForeignKey("batches.id"),
        nullable=False
    )

    source = Column(
        String(1),
        nullable=False
    )

    operation_id = Column(
        String(100),
        nullable=False
    )

    client_id = Column(
        String(100),
        nullable=False
    )

    amount = Column(
        Numeric(15, 2),
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "source",
            "operation_id",
            name="uq_operation_batch_source"
        ),
    )


class ReconciliationResult(Base):
    __tablename__ = "reconciliation_results"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(
        Integer,
        ForeignKey("batches.id"),
        nullable=False
    )

    operation_id = Column(
        String(100),
        nullable=False
    )

    result = Column(
        String(50),
        nullable=False
    )

    details = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "operation_id",
            name="uq_reconciliation_batch_operation"
        ),
    )