from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from customer_data_platform.compliance import ComplianceService
from customer_data_platform.domain import (
    CustomerEvent,
    NotFoundError,
    PlatformError,
    SegmentRule,
    ValidationError,
)
from customer_data_platform.identity import IdentityService
from customer_data_platform.ingestion import EventIngestionService
from customer_data_platform.repository import CustomerRepository
from customer_data_platform.schemas import (
    ConsentRequest,
    DeleteResponse,
    EventRequest,
    EventResponse,
    ExportResponse,
    HealthResponse,
    ProfileResponse,
    SegmentRequest,
    SegmentResponse,
)
from customer_data_platform.segmentation import SegmentationService


def create_app(repository: CustomerRepository | None = None) -> FastAPI:
    repository = repository or CustomerRepository()
    identity_service = IdentityService(repository)
    ingestion_service = EventIngestionService(repository, identity_service, batch_size=1)
    segmentation_service = SegmentationService(repository)
    compliance_service = ComplianceService(repository)

    app = FastAPI(
        title="Customer Data Platform",
        version="0.1.0",
        summary="Event ingestion, identity resolution, segmentation, and GDPR API.",
    )
    app.state.repository = repository
    app.state.ingestion_service = ingestion_service
    app.state.segmentation_service = segmentation_service
    app.state.compliance_service = compliance_service

    @app.exception_handler(PlatformError)
    async def handle_platform_error(_request: Request, exc: PlatformError) -> JSONResponse:
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, NotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/events", status_code=status.HTTP_202_ACCEPTED, response_model=EventResponse)
    def ingest_event(payload: EventRequest) -> EventResponse:
        event = CustomerEvent(
            event_type=payload.event_type,
            anonymous_id=payload.anonymous_id,
            email=payload.email,
            phone=payload.phone,
            cookie_id=payload.cookie_id,
            properties=payload.properties,
            occurred_at=payload.occurred_at,
        )
        return EventResponse.model_validate(ingestion_service.ingest(event))

    @app.get("/profiles/{profile_id}", response_model=ProfileResponse)
    def get_profile(profile_id: str) -> ProfileResponse:
        return ProfileResponse.model_validate(repository.get_profile(profile_id))

    @app.post("/segments", status_code=status.HTTP_201_CREATED, response_model=SegmentResponse)
    def create_segment(payload: SegmentRequest) -> SegmentResponse:
        segment = segmentation_service.create_segment(
            payload.name,
            [
                SegmentRule(rule.field, rule.operator, rule.value)
                for rule in payload.rules
            ],
        )
        return SegmentResponse.model_validate(segment)

    @app.post("/profiles/{profile_id}/segments/evaluate", response_model=ProfileResponse)
    def evaluate_segments(profile_id: str) -> ProfileResponse:
        return ProfileResponse.model_validate(segmentation_service.evaluate_profile(profile_id))

    @app.post("/profiles/{profile_id}/consent", response_model=ProfileResponse)
    def update_consent(profile_id: str, payload: ConsentRequest) -> ProfileResponse:
        compliance_service.update_consent(profile_id, payload.consent)
        return ProfileResponse.model_validate(repository.get_profile(profile_id))

    @app.get("/profiles/{profile_id}/export", response_model=ExportResponse)
    def export_profile(profile_id: str) -> ExportResponse:
        exported = compliance_service.export_profile(profile_id)
        return ExportResponse(**exported)

    @app.delete("/profiles/{profile_id}", response_model=DeleteResponse)
    def delete_profile(profile_id: str) -> DeleteResponse:
        compliance_service.delete_profile(profile_id)
        return DeleteResponse(deleted=True)

    return app


app = create_app()
