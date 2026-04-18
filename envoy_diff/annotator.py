"""Annotate environment variable diffs with tags, risk scores, and audit flags."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import EnvDiffResult
from envoy_diff.tagger import tag_key
from envoy_diff.auditor import is_sensitive
from envoy_diff.scorer import score_diff


@dataclass
class AnnotatedKey:
    key: str
    change_type: str  # added | removed | changed | unchanged
    old_value: Optional[str]
    new_value: Optional[str]
    tags: List[str]
    sensitive: bool
    risk_note: str


@dataclass
class AnnotatedDiff:
    entries: List[AnnotatedKey] = field(default_factory=list)

    def by_tag(self, tag: str) -> List[AnnotatedKey]:
        return [e for e in self.entries if tag in e.tags]

    def sensitive_changes(self) -> List[AnnotatedKey]:
        return [e for e in self.entries if e.sensitive and e.change_type != "unchanged"]

    def summary(self) -> str:
        total = len([e for e in self.entries if e.change_type != "unchanged"])
        sensitive = len(self.sensitive_changes())
        return f"{total} change(s), {sensitive} sensitive"


def _risk_note(change_type: str, sensitive: bool) -> str:
    if change_type == "removed" and sensitive:
        return "sensitive key removed"
    if change_type == "added" and sensitive:
        return "sensitive key introduced"
    if change_type == "changed" and sensitive:
        return "sensitive value modified"
    if change_type == "removed":
        return "key removed"
    if change_type == "added":
        return "key added"
    if change_type == "changed":
        return "value changed"
    return ""


def annotate_diff(diff: EnvDiffResult) -> AnnotatedDiff:
    entries: List[AnnotatedKey] = []

    def _entry(key: str, change_type: str, old: Optional[str], new: Optional[str]) -> AnnotatedKey:
        tags = tag_key(key)
        sensitive = is_sensitive(key)
        return AnnotatedKey(
            key=key,
            change_type=change_type,
            old_value=old,
            new_value=new,
            tags=tags,
            sensitive=sensitive,
            risk_note=_risk_note(change_type, sensitive),
        )

    for k, v in diff.added.items():
        entries.append(_entry(k, "added", None, v))
    for k, v in diff.removed.items():
        entries.append(_entry(k, "removed", v, None))
    for k, (old, new) in diff.changed.items():
        entries.append(_entry(k, "changed", old, new))
    for k, v in diff.unchanged.items():
        entries.append(_entry(k, "unchanged", v, v))

    entries.sort(key=lambda e: e.key)
    return AnnotatedDiff(entries=entries)
