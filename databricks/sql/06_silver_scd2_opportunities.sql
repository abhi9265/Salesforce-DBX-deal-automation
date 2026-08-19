CREATE TABLE IF NOT EXISTS ${catalog}.${schema}_silver.opportunities_history (
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
    source_updated_at TIMESTAMP NOT NULL,
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,
    is_current BOOLEAN NOT NULL,
    record_hash STRING NOT NULL,
    run_id STRING NOT NULL
)
USING DELTA;

-- SCD Type 2 pattern: retain the previous version and open a new current version.
-- Production execution must deduplicate the source to one latest version per opportunity.
MERGE INTO ${catalog}.${schema}_silver.opportunities_history AS target
USING ${catalog}.${schema}_bronze.opportunities_raw AS source
ON target.opportunity_id = get_json_object(source.payload, '$.Opportunity_ID')
   AND target.is_current = true
WHEN MATCHED
 AND source.source_updated_at > target.source_updated_at
 AND sha2(source.payload, 256) <> target.record_hash
THEN UPDATE SET
    effective_to = source.source_updated_at,
    is_current = false;

INSERT INTO ${catalog}.${schema}_silver.opportunities_history
SELECT
    get_json_object(payload, '$.Opportunity_ID'),
    get_json_object(payload, '$.Account_Name'),
    get_json_object(payload, '$.Opportunity_Name'),
    get_json_object(payload, '$.Country'),
    CAST(get_json_object(payload, '$.Amount') AS DECIMAL(18,2)),
    get_json_object(payload, '$.Industry'),
    get_json_object(payload, '$.Partner'),
    CAST(get_json_object(payload, '$.Close_Date') AS DATE),
    CAST(get_json_object(payload, '$.Registration_Required') AS BOOLEAN),
    get_json_object(payload, '$.Registration_Status'),
    source_updated_at,
    source_updated_at,
    NULL,
    true,
    sha2(payload, 256),
    run_id
FROM ${catalog}.${schema}_bronze.opportunities_raw s
WHERE NOT EXISTS (
    SELECT 1 FROM ${catalog}.${schema}_silver.opportunities_history h
    WHERE h.opportunity_id = get_json_object(s.payload, '$.Opportunity_ID')
      AND h.is_current = true
      AND h.source_updated_at >= s.source_updated_at
);
