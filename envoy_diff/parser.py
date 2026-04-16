"""Parser for environment variable sources (dotenv files, shell exports, raw key=value)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict


ENV_LINE_RE = re.compile(
    r'^\s*(?:export\s+)?'
    r'([A-Za-z_][A-Za-z0-9_]*)'
    r'\s*=\s*'
    r'("(?:[^"\\]|\\.)*"|\'{[^\']*}\'|[^#\r\n]*)'
    r'\s*(?:#.*)?$'
)


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
    return value


def parse_env_string(text: str) -> Dict[str, str]:
    """Parse a multi-line string of environment variable definitions.

    Supports:
    - KEY=value
    - export KEY=value
    - KEY="quoted value"
    - Inline comments (#)
    - Blank lines and comment-only lines
    """
    env: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        match = ENV_LINE_RE.match(line)
        if match:
            key, raw_value = match.group(1), match.group(2)
            env[key] = _strip_quotes(raw_value)
    return env


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Read and parse an env file from disk."""
    content = Path(path).read_text(encoding='utf-8')
    return parse_env_string(content)
