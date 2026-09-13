def reconcile_operations(source_a, source_b):
    operations_a = {
        operation.operation_id: operation
        for operation in source_a
    }

    operations_b = {
        operation.operation_id: operation
        for operation in source_b
    }

    all_operation_ids = set(operations_a.keys()) | set(operations_b.keys())

    results = []

    for operation_id in all_operation_ids:
        operation_a = operations_a.get(operation_id)
        operation_b = operations_b.get(operation_id)

        if operation_a is None:
            results.append({
                "operation_id": operation_id,
                "result": "MISSING_A",
                "details": "Operation exists only in source B"
            })
            continue

        if operation_b is None:
            results.append({
                "operation_id": operation_id,
                "result": "MISSING_B",
                "details": "Operation exists only in source A"
            })
            continue

        divergences = []

        if operation_a.client_id != operation_b.client_id:
            divergences.append("CLIENT")

        if operation_a.amount != operation_b.amount:
            divergences.append("AMOUNT")

        if operation_a.status != operation_b.status:
            divergences.append("STATUS")

        if divergences:
            results.append({
                "operation_id": operation_id,
                "result": "DIVERGENT",
                "details": ", ".join(divergences)
            })
        else:
            results.append({
                "operation_id": operation_id,
                "result": "MATCHED",
                "details": None
            })

    return results