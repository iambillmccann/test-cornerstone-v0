import uuid
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    name: str
    version: str


class AuthIdentityResponse(BaseModel):
    sub: str
    sid: str | None = None
    iss: str | None = None
    azp: str | None = None
    email: str | None = None


class AppUserProfile(BaseModel):
    """Application user profile backed by local persistence."""

    id: uuid.UUID
    email: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None


class ApiErrorDetail(BaseModel):
    field: str | None = None
    issue: str
    context: dict[str, Any] | None = None


class ApiError(BaseModel):
    code: str
    message: str
    details: list[ApiErrorDetail] = Field(default_factory=list)


class ApiErrorResponse(BaseModel):
    error: ApiError
