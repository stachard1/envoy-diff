"""Template rendering for env files — substitute variables and generate env from templates."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_VAR_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class TemplateResult:
    rendered: Dict[str, str]
    unresolved: List[str] = field(default_factory=list)
    substitutions: int = 0

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved)

    def summary(self) -> str:
        parts = [f"{self.substitutions} substitution(s) applied"]
        if self.unresolved:
            parts.append(f"{len(self.unresolved)} unresolved variable(s): {', '.join(self.unresolved)}")
        return "; ".join(parts)


def _resolve_value(value: str, context: Dict[str, str]) -> tuple[str, List[str], int]:
    """Resolve all variable references in a single value string."""
    unresolved: List[str] = []
    count = 0

    def replacer(m: re.Match) -> str:
        nonlocal count
        var_name = m.group(1) or m.group(2)
        if var_name in context:
            count += 1
            return context[var_name]
        unresolved.append(var_name)
        return m.group(0)

    resolved = _VAR_RE.sub(replacer, value)
    return resolved, unresolved, count


def render_template(
    template: Dict[str, str],
    context: Optional[Dict[str, str]] = None,
    strict: bool = False,
) -> TemplateResult:
    """Render an env template dict using the provided context.

    Args:
        template: Env dict whose values may contain ${VAR} or $VAR references.
        context: Variables to substitute. Defaults to empty dict.
        strict: If True, raise ValueError when unresolved variables are found.
    """
    ctx = dict(context or {})
    rendered: Dict[str, str] = {}
    all_unresolved: List[str] = []
    total_subs = 0

    for key, value in template.items():
        resolved, unresolved, subs = _resolve_value(value, ctx)
        rendered[key] = resolved
        all_unresolved.extend(unresolved)
        total_subs += subs

    unique_unresolved = sorted(set(all_unresolved))
    result = TemplateResult(
        rendered=rendered,
        unresolved=unique_unresolved,
        substitutions=total_subs,
    )

    if strict and result.has_unresolved:
        raise ValueError(f"Unresolved template variables: {', '.join(unique_unresolved)}")

    return result
