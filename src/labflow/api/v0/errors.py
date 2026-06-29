from typing import Literal

from pydantic import BaseModel
from pydantic_core import ErrorDetails

ErrorCode = Literal["validation_error", "conflict"]


class ApiErrorDetail(BaseModel):
    field: str
    message: str


class ApiErrorResponse(BaseModel):
    """Error envelope returned for client-facing failures."""

    status: int
    code: ErrorCode
    message: str
    details: list[ApiErrorDetail]

    @classmethod
    def from_validation_errors(
        cls,
        errors: list[ErrorDetails],
        *,
        status: int = 400,
    ) -> "ApiErrorResponse":
        """Build a 400 envelope from FastAPI/Pydantic validation errors."""
        details: list[ApiErrorDetail] = []
        for error in errors:
            loc = error.get("loc", ())
            parts = [str(part) for part in loc if part != "body"]
            field = ".".join(parts) if parts else "body"
            details.append(
                ApiErrorDetail(field=field, message=error.get("msg", "Invalid value"))
            )
        return cls(
            status=status,
            code="validation_error",
            message="Request validation failed",
            details=details,
        )

    @classmethod
    def from_conflict(
        cls,
        message: str = "Same message_id with a different request body",
    ) -> "ApiErrorResponse":
        """Build a 409 envelope for idempotency key / body mismatch."""
        return cls(status=409, code="conflict", message=message, details=[])
