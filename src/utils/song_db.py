"""
Simple JSON-based database that tracks the most played songs per server (guild).

Database schema (songs_db.json):
{
    "<guild_id>": {
        "<video_url>": {
            "title": "Song Title",
            "play_count": 5,
            "last_played": "2026-02-15T12:34:56"
        }
    }
}
"""

import json
import os
import sys
from datetime import datetime

_DB_FILENAME = "songs_db.json"


def _get_base_dir():
    """Return the project root directory.

    When frozen (exe) this is the directory containing the executable.
    When running as a script this is two levels up from this file.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_db_path():
    """Return the full path to the database file in the project root."""
    return os.path.join(_get_base_dir(), _DB_FILENAME)


def _load_db():
    """Load the database from disk. Returns an empty dict if the file doesn't exist."""
    path = _get_db_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_db(db):
    """Write the database dict back to disk."""
    path = _get_db_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def record_play(guild_id, webpage_url, title):
    """
    Record that a song was played on a given guild.
    Increments the play count by 1.
    """
    db = _load_db()
    gid = str(guild_id)

    if gid not in db:
        db[gid] = {}

    if webpage_url not in db[gid]:
        db[gid][webpage_url] = {
            "title": title,
            "play_count": 0,
            "last_played": None,
        }

    db[gid][webpage_url]["play_count"] += 1
    db[gid][webpage_url]["title"] = title  # keep title up-to-date
    db[gid][webpage_url]["last_played"] = datetime.utcnow().isoformat()

    _save_db(db)


def get_most_played(guild_id, limit=10):
    """
    Return the top `limit` most played songs for a guild.
    Each item is a dict: {"title", "webpage_url", "play_count", "last_played"}.
    """
    db = _load_db()
    gid = str(guild_id)

    if gid not in db:
        return []

    songs = []
    for url, data in db[gid].items():
        songs.append({
            "title": data.get("title", "Unknown"),
            "webpage_url": url,
            "play_count": data.get("play_count", 0),
            "last_played": data.get("last_played"),
        })

    # Sort by play_count descending, then by last_played descending
    songs.sort(key=lambda s: (s["play_count"], s["last_played"] or ""), reverse=True)
    return songs[:limit]
