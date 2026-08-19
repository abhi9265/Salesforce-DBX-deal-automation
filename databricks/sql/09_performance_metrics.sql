CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_ops.pipeline_performance (
    run_id STRING NOT NULL,
    pipeline_name STRING NOT NULL,
    stage_name STRING NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    records_processed BIGINT,
    duration_seconds DOUBLE,
    records_per_second DOUBLE
)
USING DELTA;

-- Capture stage-level throughput so optimization decisions are evidence-driven.
INSERT INTO ${catalog}.${schema}_ops.pipeline_performance
SELECT
    '${run_id}', '${pipeline_name}', '${stage_name}',
    CAST('${started_at}' AS TIMESTAMP), current_timestamp(),
    ${records_processed},
    unix_timestamp(current_timestamp()) - unix_timestamp(CAST('${started_at}' AS TIMESTAMP)),
    CASE WHEN ${records_processed} > 0
         THEN ${records_processed} / NULLIF(unix_timestamp(current_timestamp()) - unix_timestamp(CAST('${started_at}' AS TIMESTAMP)), 0)
         ELSE 0 END;
