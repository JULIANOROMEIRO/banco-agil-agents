import logging
import logging.config

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from api.api_v1.api import api_router
from core.config import settings


def api_factory() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        root_path=settings.ROOT_PATH,
        version=settings.API_VERSION,
        description="API de atendimento do Banco Ágil.",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    logging.config.dictConfig(settings.LOGGING_CONFIG)

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


app = api_factory()

_root = settings.ROOT_PATH.rstrip("/")


@app.get(
    f"{_root}/",
    description="Resposta somente para validar se a API subiu corretamente.",
    summary="Valida se API está no ar",
)
def get_index():
    return {"msg": "API está no ar!"}


@app.get(f"{_root}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{_root}/openapi.json",
        title="API Docs",
    )


@app.get(f"{_root}/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=f"{_root}/openapi.json",
        title="ReDoc",
    )


@app.get(f"{_root}/openapi.json", include_in_schema=False)
async def get_custom_openapi():
    return get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description=app.description,
    )


def run():
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = settings.LOGGING_CONFIG["formatters"]["standard"]["format"]
    uvicorn.run("main:app", log_config=log_config, reload=True)


if __name__ == "__main__":
    run()
