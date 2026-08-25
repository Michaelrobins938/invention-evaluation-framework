from engine_v17.claim_graph import decompose_claim, derive_claim_vectors


def test_us8527057_claim_has_product_and_process_vectors():
    graph = decompose_claim({
        "id": "US8527057-claim-1",
        "text": "retinal electrode array, scleral strap, hermetic flip-chip package, cable, coplanar inductive coil",
    })
    names = {d.name for d in graph.domains}
    assert {"retinal_interface", "mechanical_fixation", "electronics_packaging", "interconnect", "power_architecture"} <= names
    assert {v.kind for v in derive_claim_vectors(graph)} == {"product", "process", "dependent"}
