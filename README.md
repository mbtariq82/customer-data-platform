# customer-data-platform
1) Build an event ingestion API: accept user activity events (page views, clicks, purchases) with schema validation, buffer in a queue, and write to a data store in batches.

2) Implement identity resolution: merge events from anonymous and authenticated sessions, handle multiple identifiers (email, phone, cookie), and maintain a unified customer profile.

3) Create a segmentation engine: define segments using rules (purchased in last 30 days AND viewed category X), evaluate membership in real-time on event ingestion, and expose via API.

4) Build a GDPR compliance module: handle data subject requests (export all data, delete all data), track consent changes, implement data retention policies, and maintain audit logs.
