"""Filter environment variables by prefix, tag, or pattern."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envoy_diff.tagger import tag_key


@dataclass
class FilterResult:
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: Dict[str, str] = field(default_factory=dict)

    @property
    def count(self) -> int:
        return len(self.matched)


def filter_by_prefix(env: Dict[str, str], prefix: str) -> FilterResult:
    matched = {k: v for k, v in env.items() if k.startswith(prefix.upper())}
    excluded = {k: v for k, v in env.items() if k not in matched}
    return FilterResult(matched=matched, excluded=excluded)


def filter_by_pattern(env: Dict[str, str], pattern: str) -> FilterResult:
    rx = re.compile(pattern)
    matched = {k: v for k, v in env.items() if rx.search(k)}
    excluded = {k: v for k, v in env.items() if k not in matched}
    return FilterResult(matched=matched, excluded=excluded)


def filter_by_tag(env: Dict[str, str], tag: str) -> FilterResult:
    matched = {k: v for k, v in env.items() if tag in tag_key(k)}
    excluded = {k: v for k, v in env.items() if k not in matched}
    return FilterResult(matched=matched, excluded=excluded)


def filter_env(
    env: Dict[str, str],
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    tag: Optional[str] = None,
) -> FilterResult:
    result = env
    if prefix:
        result = filter_by_prefix(result, prefix).matched
    if pattern:
        result = filter_by_pattern(result, pattern).matched
    if tag:
        result = filter_by_tag(result, tag).matched
    excluded = {k: v for k, v in env.items() if k not in result}
    return FilterResult(matched=result, excluded=excluded)
