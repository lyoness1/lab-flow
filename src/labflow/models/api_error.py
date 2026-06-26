from typing import Literal

from pydantic import BaseModel
from pydantic_core import ErrorDetails


class ApiErrorDetail(BaseModel):
    field: str
    message: str


class ApiErrorResponse(BaseModel):
    status: int
    code: Literal["validation_error"] = "validation_error"
    message: str = "Request validation failed"
    details: list[ApiErrorDetail]

    @classmethod
    def from_validation_errors(
        cls,
        errors: list[ErrorDetails],
        *,
        status: int = 400,
    ) -> "ApiErrorResponse":
        details: list[ApiErrorDetail] = []
        for error in errors:
            loc = error.get("loc", ())
            parts = [str(part) for part in loc if part != "body"]
            field = ".".join(parts) if parts else "body"
            details.append(
                ApiErrorDetail(field=field, message=error.get("msg", "Invalid value"))
            )
        return cls(status=status, details=details)
