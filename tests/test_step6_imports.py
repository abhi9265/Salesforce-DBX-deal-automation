def test_step6_modules_import():
    import audit.repository
    import services.registration_processor

    assert audit.repository.AuditRepository is not None
    assert services.registration_processor.RegistrationProcessor is not None
