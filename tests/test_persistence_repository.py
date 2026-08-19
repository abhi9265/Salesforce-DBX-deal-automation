from audit.repository import AuditRepository
from domain.models import RegistrationRequest


def test_repository_round_trip(tmp_path):
    repo = AuditRepository(tmp_path / "audit.db")
    request = RegistrationRequest(opportunity_id="OPP-42")
    repo.save_request(request)

    loaded = repo.get_request(request.request_id)

    assert loaded is not None
    assert loaded["opportunity_id"] == "OPP-42"
    assert loaded["status"] == "NEW"


def test_event_history_is_immutable_append_only(tmp_path):
    repo = AuditRepository(tmp_path / "audit.db")
    request = RegistrationRequest(opportunity_id="OPP-42")
    repo.save_request(request)

    repo.record_transition(request.request_id, request.opportunity_id, "NEW", "ELIGIBLE")
    repo.record_transition(request.request_id, request.opportunity_id, "ELIGIBLE", "VALIDATED")

    events = repo.list_events(request.request_id)
    assert [(e["from_status"], e["to_status"]) for e in events] == [
        ("NEW", "ELIGIBLE"),
        ("ELIGIBLE", "VALIDATED"),
    ]
