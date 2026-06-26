from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from labflow.api.v0.router import router as v0_router
from labflow.models.api_error import ApiErrorResponse


def create_app() -> FastAPI:
    app = FastAPI(title="LabFlow")

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        body = ApiErrorResponse.from_validation_errors(exc.errors())
        return JSONResponse(
            status_code=body.status,
            content=body.model_dump(mode="json"),
        )

    app.include_router(v0_router)
    return app


app = create_app()
