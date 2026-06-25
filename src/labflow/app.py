from fastapi import APIRouter, FastAPI

from labflow.constants import API_V0_PREFIX


def create_app() -> FastAPI:
    app = FastAPI(title="LabFlow")
    router = APIRouter(prefix=API_V0_PREFIX)

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router)
    return app


app = create_app()
