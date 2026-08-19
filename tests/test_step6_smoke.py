def test_step6_smoke():
    from services.registration_processor import RegistrationProcessor
    from audit.repository import AuditRepository

    assert RegistrationProcessor is not None
    assert AuditRepository is not None
