from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    llm_configured: bool
