CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_bronze.opportunities_raw (
    ingestion_id STRING NOT NULL,
    source_system STRING NOT NULL,
    source_record_id STRING NOT NULL,
    payload STRING NOT NULL,
    source_updated_at TIMESTAMP,
    ingested_at TIMESTAMP NOT NULL,
    run_id STRING NOT NULL
)
USING DELTA
PARTITIONED BY (DATE(ingested_at));

-- Idempotent ingestion should use source_record_id + source_updated_at (or source CDC version)
-- as the source identity. Do not use ingestion time as the business change key.
