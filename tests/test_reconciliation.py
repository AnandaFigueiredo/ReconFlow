from decimal import Decimal

from app.schemas.schemas import OperationInput
from app.services.reconciliation import reconcile_operations


def test_reconciliation():
    source_a = [
        OperationInput(
            operation_id="OP001",
            client_id="CL001",
            amount=Decimal("10000.00"),
            status="PROCESSADA"
        ),
        OperationInput(
            operation_id="OP002",
            client_id="CL002",
            amount=Decimal("5000.00"),
            status="PROCESSADA"
        ),
        OperationInput(
            operation_id="OP003",
            client_id="CL003",
            amount=Decimal("8000.00"),
            status="PROCESSADA"
        ),
    ]

    source_b = [
        OperationInput(
            operation_id="OP001",
            client_id="CL001",
            amount=Decimal("10000.00"),
            status="PROCESSADA"
        ),
        OperationInput(
            operation_id="OP002",
            client_id="CL002",
            amount=Decimal("4900.00"),
            status="PROCESSADA"
        ),
        OperationInput(
            operation_id="OP004",
            client_id="CL004",
            amount=Decimal("3000.00"),
            status="PROCESSADA"
        ),
    ]

    results = reconcile_operations(source_a, source_b)

    results_by_id = {
        result["operation_id"]: result
        for result in results
    }

    assert results_by_id["OP001"]["result"] == "MATCHED"
    assert results_by_id["OP002"]["result"] == "DIVERGENT"
    assert results_by_id["OP002"]["details"] == "AMOUNT"
    assert results_by_id["OP003"]["result"] == "MISSING_B"
    assert results_by_id["OP004"]["result"] == "MISSING_A"