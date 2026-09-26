from pydantic import BaseModel, Field


class TopicConfig(BaseModel):
    description: str
    steps: list[str]
    actions: list[str]


class SkillConfig(BaseModel):
    name: str
    description: str
    instructions: list[str]
    topics: dict[str, TopicConfig] = Field(default_factory=dict)
