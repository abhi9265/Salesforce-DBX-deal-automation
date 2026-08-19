CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_ops.pipeline_watermarks (
    pipeline_name STRING NOT NULL,
    source_name STRING NOT NULL,
    environment STRING NOT NULL,
    last_successful_source_version TIMESTAMP,
    last_successful_run_id STRING,
    updated_at TIMESTAMP NOT NULL
)
USING DELTA;

-- Incremental extraction should read only source records newer than the last successful watermark.
-- The watermark is advanced only after Bronze ingestion and downstream quality gates succeed.
