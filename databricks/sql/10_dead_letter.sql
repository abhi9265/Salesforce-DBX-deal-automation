CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_ops.rejected_records (
    run_id STRING NOT NULL,
    dataset_name STRING NOT NULL,
    source_record_id STRING,
    rejection_reason STRING NOT NULL,
    payload STRING,
    rejected_at TIMESTAMP NOT NULL
)
USING DELTA;

-- Invalid records are isolated instead of silently dropped, enabling remediation and replay.
