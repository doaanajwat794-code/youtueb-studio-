"""Paths, YAML loading, secrets, and the ffmpeg binary."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
STATE = ROOT / "state"
PROJECTS = ROOT / "projects"
MEDIA = ROOT / "media"
LEDGER = STATE / "spend-ledger.csv"
USER_DIR = Path(os.environ.get("TWIST_VILLA_HOME", Path.home() / ".config" / "twist-villa-studio"))


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def providers() -> dict:
    return load_yaml(CONFIG / "providers.yaml")


def budget() -> dict:
    return load_yaml(CONFIG / "budget.yaml")


def project_dir(slug: str) -> Path:
    return PROJECTS / slug


def media_dir(slug: str) -> Path:
    return MEDIA / slug


def load_env() -> None:
    """Load KEY=VALUE lines from .env (git-ignored) without overriding real env vars."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def secret(name: str) -> str:
    load_env()
    value = os.environ.get(name, "")
    if not value:
        raise SystemExit(
            f"Missing secret {name}. Add it to .env (local) or the cloud environment's secrets. "
            "Never commit it to git."
        )
    return value


def ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("ffmpeg not found. Run: pip install -r requirements.txt") from exc
