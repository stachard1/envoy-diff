"""Tag environment variables with metadata labels for categorization."""

from dataclasses import dataclass, field
from typing import Dict, List, Set

BUILTIN_TAGS: Dict[str, List[str]] = {
    "sensitive": ["SECRET", "PASSWORD", "TOKEN", "API_KEY", "AUTH", "PRIVATE", "CREDENTIAL"],
    "database": ["DB_", "DATABASE", "POSTGRES", "MYSQL", "MONGO", "REDIS"],
    "network": ["HOST", "PORT", "URL", "ENDPOINT", "ADDR", "SOCKET"],
    "feature_flag": ["ENABLE_", "DISABLE_", "FEATURE_", "FLAG_"],
    "logging": ["LOG_", "LOGGING", "DEBUG", "VERBOSE"],
}


def tag_key(key: str, extra_tags: Dict[str, List[str]] | None = None) -> Set[str]:
    """Return a set of tags that apply to the given env key."""
    tags: Set[str] = set()
    rules = {**BUILTIN_TAGS, **(extra_tags or {})}
    upper = key.upper()
    for tag, patterns in rules.items():
        for pattern in patterns:
            if pattern in upper:
                tags.add(tag)
                break
    return tags


@dataclass
class TaggedEnv:
    env: Dict[str, str]
    tags: Dict[str, Set[str]] = field(default_factory=dict)

    def get_tags(self, key: str) -> Set[str]:
        return self.tags.get(key, set())

    def keys_with_tag(self, tag: str) -> List[str]:
        return [k for k, t in self.tags.items() if tag in t]


def tag_env(env: Dict[str, str], extra_tags: Dict[str, List[str]] | None = None) -> TaggedEnv:
    """Annotate every key in env with applicable tags."""
    tags = {key: tag_key(key, extra_tags) for key in env}
    return TaggedEnv(env=env, tags=tags)


def tags_summary(tagged: TaggedEnv) -> Dict[str, List[str]]:
    """Return a mapping of tag -> list of keys that carry that tag."""
    summary: Dict[str, List[str]] = {}
    for key, key_tags in tagged.tags.items():
        for tag in key_tags:
            summary.setdefault(tag, []).append(key)
    return {t: sorted(keys) for t, keys in sorted(summary.items())}
