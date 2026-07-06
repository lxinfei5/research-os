"""ResearchOS path resolution — the single place that knows the on-disk layout.

Every module asks paths.py where things live; nothing hard-codes a path. The repo ROOT can be
overridden with the ROS_ROOT env var (used by tests to point at a temp dir).

Layout (see DESIGN.md §2):

    ResearchOS/
    ├── ros/                         # this package (engine code + packaged SQL)
    ├── topics/
    │   ├── _index.yaml              # global topic registry (slug/title/aliases/status/coverage)
    │   └── <slug>/                  # ★ one directory == one independent world knowledge
    │       ├── topic.yaml
    │       ├── knowledge.db         # canonical L0–L3 (frozen baseline + migrations)
    │       ├── sources.db           # replayable raw-intake sidecar
    │       ├── cache/<hash>.md       # per-topic link + cached-text snapshots
    │       ├── transcripts/  screenshots/  artifacts/  reports/  snapshots/
    ├── library/sources/<sha256>.json  # global content-addressed original store
    └── .ros/active                  # pointer to the active topic slug
"""
from __future__ import annotations

import os
from pathlib import Path

# ── repo root ────────────────────────────────────────────────────────────────
_PKG_DIR = Path(__file__).resolve().parent            # …/ResearchOS/ros
_DEFAULT_ROOT = _PKG_DIR.parent                        # …/ResearchOS


def root() -> Path:
    """Repo root. ROS_ROOT env overrides (tests, alternate data dirs)."""
    env = os.environ.get("ROS_ROOT")
    return Path(env).expanduser().resolve() if env else _DEFAULT_ROOT


# ── packaged engine assets (always under ros/, never under the data root) ────
PKG_DIR = _PKG_DIR
SCHEMA_KNOWLEDGE_PATH = _PKG_DIR / "storage" / "schema_knowledge.sql"
TRIGGERS_PATH = _PKG_DIR / "storage" / "triggers.sql"
VOCAB_SEED_PATH = _PKG_DIR / "storage" / "vocab_seed.sql"
MIGRATIONS_DIR = _PKG_DIR / "storage" / "migrations"


# ── data tree (under root(), honoring ROS_ROOT) ──────────────────────────────
def topics_dir() -> Path:
    return root() / "topics"


def index_path() -> Path:
    return topics_dir() / "_index.yaml"


def shared_dir() -> Path:
    return topics_dir() / "_shared"


def shared_method_db() -> Path:
    """Optional cross-topic method store (M0/M1 only, opt-in)."""
    return shared_dir() / "method.db"


def active_pointer() -> Path:
    return root() / ".ros" / "active"


def library_dir() -> Path:
    return root() / "library"


def library_sources_dir() -> Path:
    return library_dir() / "sources"


def library_source_path(content_hash: str) -> Path:
    return library_sources_dir() / f"{content_hash}.json"


def logs_dir() -> Path:
    return root() / "logs"


# ── per-topic paths ──────────────────────────────────────────────────────────
def topic_dir(slug: str) -> Path:
    return topics_dir() / slug


def knowledge_db(slug: str) -> Path:
    return topic_dir(slug) / "knowledge.db"


def sources_db(slug: str) -> Path:
    return topic_dir(slug) / "sources.db"


def topic_yaml(slug: str) -> Path:
    return topic_dir(slug) / "topic.yaml"


def cache_dir(slug: str) -> Path:
    return topic_dir(slug) / "cache"


def cache_path(slug: str, content_hash: str) -> Path:
    return cache_dir(slug) / f"{content_hash}.md"


def transcripts_dir(slug: str) -> Path:
    return topic_dir(slug) / "transcripts"


def screenshots_dir(slug: str) -> Path:
    return topic_dir(slug) / "screenshots"


def reports_dir(slug: str) -> Path:
    return topic_dir(slug) / "reports"


def report_sessions_dir(slug: str) -> Path:
    return reports_dir(slug) / "sessions"


def artifacts_dir(slug: str) -> Path:
    return topic_dir(slug) / "artifacts"


def snapshots_dir(slug: str) -> Path:
    return topic_dir(slug) / "snapshots"


def latest_snapshot_path(slug: str) -> Path | None:
    """Most recent *.sql snapshot for a topic (sorted by name = YYYY-MM-DD), or None.

    Snapshots are the git-committed durable artifact; the live knowledge.db is gitignored.
    Used by ensure_knowledge_db() to auto-restore the live DB in worktree/fresh-clone mode.
    """
    d = snapshots_dir(slug)
    if not d.is_dir():
        return None
    snaps = sorted(d.glob("*.sql"))
    return snaps[-1] if snaps else None


# Sub-dirs created when a topic is scaffolded.
TOPIC_SUBDIRS = (
    cache_dir, transcripts_dir, screenshots_dir,
    reports_dir, report_sessions_dir, artifacts_dir, snapshots_dir,
)


def ensure_topic_tree(slug: str) -> None:
    """Create the per-topic directory skeleton (idempotent)."""
    topic_dir(slug).mkdir(parents=True, exist_ok=True)
    for fn in TOPIC_SUBDIRS:
        fn(slug).mkdir(parents=True, exist_ok=True)
    library_sources_dir().mkdir(parents=True, exist_ok=True)
