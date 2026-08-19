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

-- Fail the pipeline when critical business keys or freshness assumptions are violated.
INSERT INTO ${catalog}.${schema}_ops.data_quality_results
SELECT
    '${run_id}', 'silver.opportunities', 'opportunity_id_not_null', COUNT(*),
    SUM(CASE WHEN opportunity_id IS NULL THEN 1 ELSE 0 END),
    COALESCE(SUM(CASE WHEN opportunity_id IS NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 0D),
    CASE WHEN SUM(CASE WHEN opportunity_id IS NULL THEN 1 ELSE 0 END) = 0 THEN 'PASS' ELSE 'FAIL' END,
    current_timestamp()
FROM ${catalog}.${schema}_silver.opportunities;

INSERT INTO ${catalog}.${schema}_ops.data_quality_results
SELECT
    '${run_id}', 'silver.opportunities', 'amount_non_negative', COUNT(*),
    SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END),
    COALESCE(SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 0D),
    CASE WHEN SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) = 0 THEN 'PASS' ELSE 'FAIL' END,
    current_timestamp()
FROM ${catalog}.${schema}_silver.opportunities;

INSERT INTO ${catalog}.${schema}_ops.data_quality_results
SELECT
    '${run_id}', 'silver.opportunities', 'current_version_unique', COUNT(*),
    COALESCE(SUM(CASE WHEN current_count > 1 THEN current_count - 1 ELSE 0 END), 0),
    COALESCE(SUM(CASE WHEN current_count > 1 THEN current_count - 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 0D),
    CASE WHEN MAX(current_count) <= 1 THEN 'PASS' ELSE 'FAIL' END,
    current_timestamp()
FROM (
    SELECT opportunity_id, COUNT(*) AS current_count
    FROM ${catalog}.${schema}_silver.opportunities_history
    WHERE is_current = true
    GROUP BY opportunity_id
);
