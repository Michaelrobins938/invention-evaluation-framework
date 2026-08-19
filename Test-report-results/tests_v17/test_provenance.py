from engine_v17.provenance import validate_query_match, validate_time_bucket_labels


def test_chart_and_narrative_queries_must_match():
    assert validate_query_match("A61N 1/18 AND retinal", "A61N1/0543 AND retinal")
    assert not validate_query_match("A61N1/0543 AND retinal", "A61N1/0543 AND retinal")


def test_current_partial_bucket_must_be_marked():
    errors = validate_time_bucket_labels(["2022–2025", "2025–2026 YTD"], "2026-08-15")
    assert "current_partial_bucket_not_marked:2022–2025" not in errors
    assert not any("2025–2026 YTD" in error for error in errors)
