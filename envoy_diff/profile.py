"""Profile management: save and load named env profiles for comparison."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_PROFILE_DIR = Path.home() / ".envoy_diff" / "profiles"


def _profile_path(name: str, profile_dir: Path) -> Path:
    return profile_dir / f"{name}.json"


def save_profile(name: str, env: Dict[str, str], profile_dir: Path = DEFAULT_PROFILE_DIR) -> Path:
    """Save an env dict as a named profile. Returns the path written."""
    profile_dir.mkdir(parents=True, exist_ok=True)
    path = _profile_path(name, profile_dir)
    with open(path, "w") as f:
        json.dump({"name": name, "env": env}, f, indent=2)
    return path


def load_profile(name: str, profile_dir: Path = DEFAULT_PROFILE_DIR) -> Optional[Dict[str, str]]:
    """Load a named profile. Returns None if not found."""
    path = _profile_path(name, profile_dir)
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    return data.get("env", {})


def list_profiles(profile_dir: Path = DEFAULT_PROFILE_DIR):
    """Return list of saved profile names."""
    if not profile_dir.exists():
        return []
    return [p.stem for p in sorted(profile_dir.glob("*.json"))]


def delete_profile(name: str, profile_dir: Path = DEFAULT_PROFILE_DIR) -> bool:
    """Delete a named profile. Returns True if deleted, False if not found."""
    path = _profile_path(name, profile_dir)
    if not path.exists():
        return False
    os.remove(path)
    return True


def profile_exists(name: str, profile_dir: Path = DEFAULT_PROFILE_DIR) -> bool:
    return _profile_path(name, profile_dir).exists()
