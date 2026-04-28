"""Pydantic schemas for the Weave API server."""

from pydantic import BaseModel, field_validator


class JobCreateParams(BaseModel):
    """Parameters passed when creating a new conversion job."""

    provider: str = "gemini"
    model: str = "gemini-2.5-flash"
    api_key: str
    language: str = "繁體中文"
    export_pdf: bool = True

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = {"gemini", "openai", "claude", "anthropic"}
        if v.lower() not in allowed:
            raise ValueError(
                f"provider must be one of {sorted(allowed)}, got {v!r}"
            )
        return v.lower()


class JobCreateResponse(BaseModel):
    """Returned after successfully creating a job."""

    job_id: str


class JobResultResponse(BaseModel):
    """Returned when a job has completed."""

    markdown: str
    output_dir_name: str  # e.g. "20260426_123456"
    has_pdf: bool


class SSEEvent(BaseModel):
    """Shape of a single Server-Sent Event payload."""

    type: str   # "progress" | "complete" | "error"
    step: str   # machine-readable step identifier
    detail: str = ""
