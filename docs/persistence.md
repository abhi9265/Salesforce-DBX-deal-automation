# Persistence model

The workflow persists two related concepts:

1. **Registration request** — the current materialized state used by the application.
2. **Registration event** — an immutable record of every state transition.

This gives the system both fast current-state reads and a reconstructable audit history.

```text
registration_requests
  request_id (PK)
  opportunity_id (unique)
  status
  validation_errors
  approval/submission fields
  created_at / updated_at

registration_events
  event_id (PK)
  request_id (FK)
  opportunity_id
  from_status
  to_status
  actor
  reason
  occurred_at
  metadata
```

SQLite is intentionally used for the local MVP. A production deployment can replace the repository implementation with a managed transactional store without changing the workflow/domain layer.
