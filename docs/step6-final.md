# Step 6 final scope

Step 6 is limited to reliable downstream submission behavior. It does not add Bronze/Silver/Gold layers, Kafka, ML or other infrastructure that the business problem does not require.

The target is a clear deterministic flow: Salesforce opportunity -> canonical deal -> validation -> approval -> DBX mapping -> registration submission -> audit.
