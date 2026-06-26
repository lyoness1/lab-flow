from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from labflow.api.v0.router import router as v0_router


def create_app() -> FastAPI:
    app = FastAPI(title="LabFlow")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    app.include_router(v0_router)
    return app


app = create_app()
