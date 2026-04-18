"""Group environment variables by prefix or tag for organized reporting."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envoy_diff.tagger import tag_key


@dataclass
class EnvGroup:
    name: str
    keys: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.keys)


def _prefix(key: str) -> str:
    """Return the first segment of a snake_case/UPPER_CASE key."""
    return key.split("_")[0].upper()


def group_by_prefix(env: Dict[str, str]) -> Dict[str, EnvGroup]:
    """Group env keys by their prefix (e.g. DB_HOST -> DB)."""
    groups: Dict[str, EnvGroup] = {}
    for key in env:
        p = _prefix(key)
        if p not in groups:
            groups[p] = EnvGroup(name=p)
        groups[p].keys.append(key)
    return groups


def group_by_tag(env: Dict[str, str]) -> Dict[str, EnvGroup]:
    """Group env keys by their semantic tag."""
    groups: Dict[str, EnvGroup] = {}
    for key in env:
        tags = tag_key(key)
        label = tags[0] if tags else "other"
        if label not in groups:
            groups[label] = EnvGroup(name=label)
        groups[label].keys.append(key)
    return groups


def group_summary(groups: Dict[str, EnvGroup]) -> str:
    lines = []
    for name, grp in sorted(groups.items()):
        lines.append(f"{name}: {len(grp)} key(s) -> {', '.join(sorted(grp.keys))}")
    return "\n".join(lines)
