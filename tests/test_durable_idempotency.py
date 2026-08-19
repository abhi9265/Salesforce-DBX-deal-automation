from audit.processed_deals import SQLiteProcessedDealStore


def test_processed_deal_store_survives_new_instance(tmp_path):
    path = tmp_path / "idempotency.db"
    first = SQLiteProcessedDealStore(path)
    first.mark_processed("OPP-001", "fingerprint-1")

    second = SQLiteProcessedDealStore(path)
    assert second.has_processed("OPP-001", "fingerprint-1") is True
    assert second.has_processed("OPP-001", "fingerprint-2") is False
