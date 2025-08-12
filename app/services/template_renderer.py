from __future__ import annotations
from typing import Mapping
from jinja2.sandbox import SandboxedEnvironment


env = SandboxedEnvironment(autoescape=True)


def render_template_string(template: str, variables: Mapping[str, object]) -> str:
    compiled = env.from_string(template)
    return compiled.render(**variables)
