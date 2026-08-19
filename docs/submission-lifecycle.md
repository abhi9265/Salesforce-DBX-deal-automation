# Submission lifecycle

The registration workflow treats downstream submission as a stateful business operation.

```text
APPROVED
   |
   +---- accepted + registration number ----> SUBMITTED -> REGISTERED
   |
   +---- rejected / failed -----------------> SUBMISSION_FAILED
   |
   +---- accepted without confirmation -----> SUBMISSION_UNKNOWN
```

A request is only marked `REGISTERED` after the downstream adapter returns a registration number. Failed or unknown outcomes remain explicit so they can be retried or investigated rather than being silently treated as success.

Each submission transition can be written to the audit repository with the request ID, opportunity ID, previous state, new state, reason and timestamp.
