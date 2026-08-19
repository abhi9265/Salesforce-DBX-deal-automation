CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_ops.pipeline_audit (
    run_id STRING NOT NULL,
    pipeline_name STRING NOT NULL,
    environment STRING NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    records_in BIGINT,
    records_out BIGINT,
    records_rejected BIGINT,
    watermark STRING,
    status STRING NOT NULL,
    error_message STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_ops.data_quality_results (
    run_id STRING NOT NULL,
    dataset_name STRING NOT NULL,
    rule_name STRING NOT NULL,
    records_checked BIGINT NOT NULL,
    records_failed BIGINT NOT NULL,
    failure_rate DOUBLE NOT NULL,
    status STRING NOT NULL,
    evaluated_at TIMESTAMP NOT NULL
)
USING DELTA;
