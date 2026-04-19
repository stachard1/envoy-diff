"""Transform env dicts: rename keys, remap values, apply templates."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import re


@dataclass
class TransformRule:
    key_pattern: str
    action: str  # 'rename', 'remap', 'delete', 'set'
    target: Optional[str] = None   # new key name or static value
    value_map: Optional[Dict[str, str]] = None  # for remap
    transform_fn: Optional[Callable[[str], str]] = None


@dataclass
class TransformResult:
    env: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def apply_transforms(env: Dict[str, str], rules: List[TransformRule]) -> TransformResult:
    result = dict(env)
    applied: List[str] = []
    skipped: List[str] = []

    for rule in rules:
        matched = [k for k in list(result.keys()) if re.fullmatch(rule.key_pattern, k)]
        if not matched:
            skipped.append(rule.key_pattern)
            continue

        for key in matched:
            if rule.action == 'delete':
                del result[key]
                applied.append(f"delete:{key}")

            elif rule.action == 'rename' and rule.target:
                result[rule.target] = result.pop(key)
                applied.append(f"rename:{key}->{rule.target}")

            elif rule.action == 'set' and rule.target is not None:
                result[key] = rule.target
                applied.append(f"set:{key}={rule.target}")

            elif rule.action == 'remap' and rule.value_map:
                old_val = result[key]
                result[key] = rule.value_map.get(old_val, old_val)
                applied.append(f"remap:{key}")

            elif rule.action == 'transform' and rule.transform_fn:
                result[key] = rule.transform_fn(result[key])
                applied.append(f"transform:{key}")

            else:
                skipped.append(f"{rule.action}:{key}")

    return TransformResult(env=result, applied=applied, skipped=skipped)
