CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_gold.registration_metrics_daily (
    metric_date DATE NOT NULL,
    eligible_deals BIGINT NOT NULL,
    validation_failed BIGINT NOT NULL,
    ready_for_review BIGINT NOT NULL,
    approved BIGINT NOT NULL,
    submitted BIGINT NOT NULL,
    registered BIGINT NOT NULL,
    rejected BIGINT NOT NULL,
    avg_registration_amount DECIMAL(18,2),
    refreshed_at TIMESTAMP NOT NULL
)
USING DELTA;

-- Gold is intentionally business-facing: it should not expose raw Salesforce payloads.
