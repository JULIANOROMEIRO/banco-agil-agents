import shutil
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from core.config import settings
from main import app
from services import session_service

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(autouse=True)
def isolar_dados(tmp_path, monkeypatch):
    destino = tmp_path / "data"
    shutil.copytree(DATA_DIR, destino)
    monkeypatch.setattr(settings, "DATA_DIR", str(destino))
    session_service.limpar()
    yield


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
