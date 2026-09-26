import logging

from fastapi import APIRouter

from core.config import settings
from schemas.health_schema import HealthStatus

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    """Informa se a API está no ar e se a chave do modelo foi configurada."""
    logger.info("Consultando health")
    return HealthStatus(
        status="ok",
        llm_configured=bool(settings.OPENROUTER_API_KEY),
    )
