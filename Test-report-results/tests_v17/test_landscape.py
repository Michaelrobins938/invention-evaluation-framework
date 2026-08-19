from engine_v17.landscape import infer_landscape, normalize_landscape, record_retrieval


def test_retrieval_volume_is_distinct_from_normalized_family_count():
    retrieval = record_retrieval([
        {"publication_number": "A", "family_id": "F1", "assignee": "Acme"},
        {"publication_number": "B", "family_id": "F1", "assignee": "Acme Inc."},
    ], {"query": "retinal"})
    landscape = normalize_landscape(retrieval)
    inference = infer_landscape(landscape)
    assert inference.retrieval_count == 2
    assert inference.normalized_family_count == 1
    assert inference.decision_value == "low"
