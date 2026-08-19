CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_silver.opportunities (
    opportunity_id STRING NOT NULL,
    account_name STRING,
    opportunity_name STRING,
    country STRING,
    amount DECIMAL(18,2),
    industry STRING,
    partner STRING,
    close_date DATE,
    registration_required BOOLEAN,
    registration_status STRING,
    source_updated_at TIMESTAMP,
    processed_at TIMESTAMP NOT NULL,
    run_id STRING NOT NULL,
    record_hash STRING NOT NULL
)
USING DELTA;

-- Silver is the canonical, typed opportunity model consumed by the workflow.
-- Production ingestion should MERGE only new/changed source versions into this table.
