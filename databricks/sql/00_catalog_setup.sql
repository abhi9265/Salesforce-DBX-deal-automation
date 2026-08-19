-- Environment-aware Unity Catalog bootstrap.
-- Execute with deployment substitution for catalog/schema names.

CREATE CATALOG IF NOT EXISTS ${catalog};

CREATE SCHEMA IF NOT EXISTS ${catalog}.${schema};
