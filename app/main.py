from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.logging_config import logger
from app.models.models import (
    Batch,
    Operation,
    ReconciliationResult,
)
from app.schemas.schemas import ReconciliationRequest
from app.services.reconciliation import reconcile_operations
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ReconFlow API",
    description="Automated Reconciliation & Exception Management",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://recon-flow-zeta.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "ReconFlow API"}


@app.post("/reconciliations", status_code=201)
def create_reconciliation(
    request: ReconciliationRequest,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Starting reconciliation batch={request.batch_code}"
    )

    existing_batch = (
        db.query(Batch)
        .filter(Batch.batch_code == request.batch_code)
        .first()
    )

    if existing_batch:
        logger.warning(
            f"Duplicate batch detected batch={request.batch_code}"
        )

        raise HTTPException(
            status_code=409,
            detail="Batch already processed",
        )

    try:
        results = reconcile_operations(
            request.source_a,
            request.source_b,
        )

        total_matched = sum(
            1
            for result in results
            if result["result"] == "MATCHED"
        )

        total_divergent = sum(
            1
            for result in results
            if result["result"] == "DIVERGENT"
        )

        total_missing = sum(
            1
            for result in results
            if result["result"] in ["MISSING_A", "MISSING_B"]
        )

        batch = Batch(
            batch_code=request.batch_code,
            status="PROCESSING",
            total_a=len(request.source_a),
            total_b=len(request.source_b),
            total_matched=total_matched,
            total_divergent=total_divergent,
            total_missing=total_missing,
        )

        db.add(batch)

        # Gera o ID do batch antes do commit.
        db.flush()

        for operation in request.source_a:
            db.add(
                Operation(
                    batch_id=batch.id,
                    source="A",
                    operation_id=operation.operation_id,
                    client_id=operation.client_id,
                    amount=operation.amount,
                    status=operation.status,
                )
            )

        for operation in request.source_b:
            db.add(
                Operation(
                    batch_id=batch.id,
                    source="B",
                    operation_id=operation.operation_id,
                    client_id=operation.client_id,
                    amount=operation.amount,
                    status=operation.status,
                )
            )

        for result in results:
            db.add(
                ReconciliationResult(
                    batch_id=batch.id,
                    operation_id=result["operation_id"],
                    result=result["result"],
                    details=result["details"],
                )
            )

        batch.status = "COMPLETED"

        db.commit()
        db.refresh(batch)

        logger.info(
            f"Reconciliation completed "
            f"batch={batch.batch_code} "
            f"matched={batch.total_matched} "
            f"divergent={batch.total_divergent} "
            f"missing={batch.total_missing}"
        )

        return {
            "batch_id": batch.id,
            "batch_code": batch.batch_code,
            "total_a": batch.total_a,
            "total_b": batch.total_b,
            "total_matched": batch.total_matched,
            "total_divergent": batch.total_divergent,
            "total_missing": batch.total_missing,
            "status": batch.status,
            "results": results,
        }

    except Exception as error:
        db.rollback()

        logger.exception(
            f"Reconciliation failed "
            f"batch={request.batch_code} "
            f"error={error}"
        )

        raise


@app.get("/reconciliations")
def list_reconciliations(
    db: Session = Depends(get_db),
):
    batches = (
        db.query(Batch)
        .order_by(Batch.created_at.desc())
        .all()
    )

    return [
        {
            "batch_id": batch.id,
            "batch_code": batch.batch_code,
            "total_a": batch.total_a,
            "total_b": batch.total_b,
            "total_matched": batch.total_matched,
            "total_divergent": batch.total_divergent,
            "total_missing": batch.total_missing,
            "status": batch.status,
            "created_at": batch.created_at,
        }
        for batch in batches
    ]


@app.get("/reconciliations/{batch_id}")
def get_reconciliation(
    batch_id: int,
    db: Session = Depends(get_db),
):
    batch = (
        db.query(Batch)
        .filter(Batch.id == batch_id)
        .first()
    )

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Batch not found",
        )

    return {
        "batch_id": batch.id,
        "batch_code": batch.batch_code,
        "total_a": batch.total_a,
        "total_b": batch.total_b,
        "total_matched": batch.total_matched,
        "total_divergent": batch.total_divergent,
        "total_missing": batch.total_missing,
        "status": batch.status,
        "created_at": batch.created_at,
    }


@app.get("/reconciliations/{batch_id}/exceptions")
def get_reconciliation_exceptions(
    batch_id: int,
    db: Session = Depends(get_db),
):
    batch = (
        db.query(Batch)
        .filter(Batch.id == batch_id)
        .first()
    )

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Batch not found",
        )

    exceptions = (
        db.query(ReconciliationResult)
        .filter(
            ReconciliationResult.batch_id == batch_id,
            ReconciliationResult.result != "MATCHED",
        )
        .all()
    )

    return {
        "batch_id": batch.id,
        "batch_code": batch.batch_code,
        "total_exceptions": len(exceptions),
        "exceptions": [
            {
                "operation_id": item.operation_id,
                "result": item.result,
                "details": item.details,
            }
            for item in exceptions
        ],
    }