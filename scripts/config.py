"""
config.py — Central configuration for TikTok automation suite.
All tunables live here. User-facing settings persist to output/settings.json.
"""

import os
import json

# ─── Path Resolution ─────────────────────────────────────────────
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")

# Ensure directories exist on import
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

# ─── Settings Persistence ────────────────────────────────────────
SETTINGS_FILE = os.path.join(OUTPUT_DIR, "settings.json")

_DEFAULTS = {
    "headless_mode": True,
    "use_proxies": False,
}


def load_settings() -> dict:
    """Load saved settings from settings.json, falling back to defaults."""
    settings = dict(_DEFAULTS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
                saved = json.load(fh)
                settings.update(saved)
        except (json.JSONDecodeError, OSError):
            pass
    return settings


def save_settings(settings: dict):
    """Write current settings to settings.json."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)


# ─── Load on Import ──────────────────────────────────────────────
_user_settings = load_settings()

# ─── Browser Settings ────────────────────────────────────────────
HEADLESS_MODE = _user_settings["headless_mode"]
BROWSER_TIMEOUT = 30
IMPLICIT_WAIT = 10
PAGE_LOAD_STRATEGY = "eager"

# ─── Proxy Settings ──────────────────────────────────────────────
USE_PROXIES = _user_settings["use_proxies"]
PROXY_FILE = os.path.join(INPUT_DIR, "proxies.txt")
COOKIE_FILE = os.path.join(INPUT_DIR, "cookies.json")
PROXY_ROTATION_INTERVAL = 5

# ─── Rate Limiting ───────────────────────────────────────────────
MIN_ACTION_DELAY = 2.0
MAX_ACTION_DELAY = 5.0
BATCH_SIZE = 10
BATCH_PAUSE_MIN = 15.0
BATCH_PAUSE_MAX = 30.0

# ─── Account Settings ────────────────────────────────────────────
ACCOUNT_INPUT_FILE = os.path.join(INPUT_DIR, "accounts.txt")
ACCOUNT_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "accounts.txt")

# ─── View Bot Settings ───────────────────────────────────────────
VIEW_DURATION_MIN = 5
VIEW_DURATION_MAX = 15

# ─── Comment Bot Settings ────────────────────────────────────────
COMMENT_POOL = [
    "This is fire 🔥", "No way 😂", "Absolutely love this ❤️",
    "Can't stop watching 👀", "This hit different fr", "W content 🏆",
    "Underrated creator tbh", "The talent jumped out 💯",
    "Bro cooked with this one 🍳", "Need more of this energy ⚡",
    "Main character vibes fr 🎬", "This made my whole day 😭",
    "POV: you found peak content", "Obsessed with this 💅",
    "The way I screamed 💀", "Living for this content rn",
    "Someone give this person a medal 🥇", "Certified banger 🎵",
    "How is this not viral yet??", "Take my follow immediately 🫡",
]

# ─── Follow Bot Settings ─────────────────────────────────────────
UNFOLLOW_AFTER = False
UNFOLLOW_DELAY_HOURS = 24

# ─── Logging ─────────────────────────────────────────────────────
LOG_FILE = os.path.join(OUTPUT_DIR, "automation.log")
LOG_LEVEL = "INFO"
VERBOSE_CONSOLE = True


def reload():
    """Reload settings from disk and update module-level globals."""
    global HEADLESS_MODE, USE_PROXIES, _user_settings
    _user_settings = load_settings()
    HEADLESS_MODE = _user_settings["headless_mode"]
    USE_PROXIES = _user_settings["use_proxies"]
