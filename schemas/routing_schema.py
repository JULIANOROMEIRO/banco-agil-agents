from typing import Literal

from pydantic import BaseModel, Field


class RoutingDecision(BaseModel):
    next_agent: Literal["credit", "exchange", "finish"]
    reason: str = Field(min_length=1)
