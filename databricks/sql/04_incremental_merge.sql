-- Template for incremental Silver processing.
-- The source must provide a stable change version (source_updated_at or CDC sequence).

MERGE INTO ${catalog}.${schema}_silver.opportunities AS target
USING ${catalog}.${schema}_bronze.opportunities_raw AS source
ON target.opportunity_id = get_json_object(source.payload, '$.Opportunity_ID')
WHEN MATCHED AND source.source_updated_at > target.source_updated_at THEN
  UPDATE SET
    account_name = get_json_object(source.payload, '$.Account_Name'),
    opportunity_name = get_json_object(source.payload, '$.Opportunity_Name'),
    country = get_json_object(source.payload, '$.Country'),
    amount = CAST(get_json_object(source.payload, '$.Amount') AS DECIMAL(18,2)),
    industry = get_json_object(source.payload, '$.Industry'),
    partner = get_json_object(source.payload, '$.Partner'),
    close_date = CAST(get_json_object(source.payload, '$.Close_Date') AS DATE),
    registration_required = CAST(get_json_object(source.payload, '$.Registration_Required') AS BOOLEAN),
    registration_status = get_json_object(source.payload, '$.Registration_Status'),
    source_updated_at = source.source_updated_at,
    processed_at = current_timestamp(),
    run_id = source.run_id,
    record_hash = sha2(source.payload, 256)
WHEN NOT MATCHED THEN
  INSERT (
    opportunity_id, account_name, opportunity_name, country, amount,
    industry, partner, close_date, registration_required, registration_status,
    source_updated_at, processed_at, run_id, record_hash
  ) VALUES (
    get_json_object(source.payload, '$.Opportunity_ID'),
    get_json_object(source.payload, '$.Account_Name'),
    get_json_object(source.payload, '$.Opportunity_Name'),
    get_json_object(source.payload, '$.Country'),
    CAST(get_json_object(source.payload, '$.Amount') AS DECIMAL(18,2)),
    get_json_object(source.payload, '$.Industry'),
    get_json_object(source.payload, '$.Partner'),
    CAST(get_json_object(source.payload, '$.Close_Date') AS DATE),
    CAST(get_json_object(source.payload, '$.Registration_Required') AS BOOLEAN),
    get_json_object(source.payload, '$.Registration_Status'),
    source.source_updated_at,
    current_timestamp(),
    source.run_id,
    sha2(source.payload, 256)
  );
