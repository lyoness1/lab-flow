from fastapi import APIRouter, FastAPI

from labflow.constants import API_V0_PREFIX
from labflow.models.health import HealthResponse


def create_app() -> FastAPI:
    app = FastAPI(title="LabFlow")
    router = APIRouter(prefix=API_V0_PREFIX)

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    app.include_router(router)
    return app


app = create_app()
