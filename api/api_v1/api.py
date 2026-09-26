"""Agrega os routers da versão 1 da API."""

from fastapi import APIRouter

from api.api_v1.endpoints import health, sessions

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
