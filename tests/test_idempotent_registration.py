from dataclasses import dataclass, replace

from domain.models import Deal, RegistrationRequest
from services.idempotency import deal_fingerprint
from services.registration_processor import RegistrationProcessor


@dataclass
class Result:
    accepted: bool
    message: str = "ok"


class MemoryStore:
    def __init__(self):
        self.values = set()

    def has_processed(self, opportunity_id, fingerprint):
        return (opportunity_id, fingerprint) in self.values

    def mark_processed(self, opportunity_id, fingerprint):
        self.values.add((opportunity_id, fingerprint))


class Gateway:
    def __init__(self):
        self.calls = 0
        self.request_ids = []

    def submit(self, payload, request_id):
        self.calls += 1
        self.request_ids.append(request_id)
        return Result(accepted=True)


def deal():
    return Deal(
        opportunity_id="OPP-001", account_name="Acme", opportunity_name="Platform",
        country="India", amount=100000, industry="Technology", partner="Databricks",
        close_date="2026-09-30", registration_required=True,
        registration_status="Not Registered", source_system="test",
    )


def test_same_deal_version_is_submitted_once():
    store, gateway = MemoryStore(), Gateway()
    processor = RegistrationProcessor(store, gateway)
    request = RegistrationRequest("OPP-001")
    first = processor.process(deal(), request, {"customer_name": "Acme"})
    second = processor.process(deal(), request, {"customer_name": "Acme"})

    assert first.processed is True
    assert second.skipped is True
    assert gateway.calls == 1
    assert gateway.request_ids == [request.request_id]


def test_business_change_produces_new_fingerprint():
    original = deal()
    changed = replace(original, amount=125000)
    assert deal_fingerprint(original) != deal_fingerprint(changed)
