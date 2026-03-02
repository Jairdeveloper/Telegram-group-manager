"""Factory for modular FastAPI app."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import create_chat_router


def create_api_app(
    *,
    app_name: str,
    app_version: str,
    app_description: str,
    agent,
    storage,
) -> FastAPI:
    app = FastAPI(
        title=app_name,
        version=app_version,
        description=app_description,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": app_version}

    app.include_router(
        create_chat_router(
            agent=agent,
            storage=storage,
            app_name=app_name,
            app_version=app_version,
        ),
        prefix="/api/v1",
    )
    return app

