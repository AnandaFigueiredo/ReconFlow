from decimal import Decimal

from pydantic import BaseModel, Field 


class OperationInput(BaseModel):
    operation_id: str = Field(min_length=1)
    client_id: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    status: str = Field(min_length=1)

class ReconciliationRequest(BaseModel):
    batch_code: str
    source_a: list[OperationInput]
    source_b: list[OperationInput]

class ReconciliationSummary(BaseModel):
    batch_code: str
    total_a: int
    total_b: int
    total_matched: int
    total_divergent: int
    total_missing: int
    status: str