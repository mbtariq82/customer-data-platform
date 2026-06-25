# Customer Data Platform

Training implementation of a customer data platform. It supports event
ingestion, identity resolution, segmentation, consent changes, export, deletion,
and audit logging.

## Features

- Validate and ingest page view, click, purchase, and consent events.
- Resolve profiles across anonymous IDs, email, phone, and cookie identifiers.
- Buffer events and flush them to an in-memory data store in batches.
- Define segments with simple rules over events and properties.
- Export or delete subject data and maintain audit entries for compliance.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
uvicorn customer_data_platform.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API docs.

## Test

```bash
pytest
```

## Key endpoints

- `POST /events`
- `GET /profiles/{profile_id}`
- `POST /segments`
- `POST /profiles/{profile_id}/segments/evaluate`
- `POST /profiles/{profile_id}/consent`
- `GET /profiles/{profile_id}/export`
- `DELETE /profiles/{profile_id}`
