"""Carrega o YAML declarativo de um agente."""

from pathlib import Path

import yaml

from schemas.skill_schema import SkillConfig

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"


def load_skill(name: str) -> SkillConfig:
    caminho = AGENTS_DIR / name / "skill.yaml"
    with caminho.open(encoding="utf-8") as arquivo:
        dados = yaml.safe_load(arquivo)
    return SkillConfig.model_validate(dados)


def render_skill(skill: SkillConfig) -> str:
    linhas = [skill.description.strip(), "", "Instruções:"]
    linhas.extend(f"- {instrucao}" for instrucao in skill.instructions)
    for nome, topico in skill.topics.items():
        linhas.append("")
        linhas.append(f"Tópico {nome}: {topico.description.strip()}")
        linhas.append("Passos: " + "; ".join(topico.steps))
        linhas.append("Actions: " + ", ".join(topico.actions))
    return "\n".join(linhas)
