import os
import sys


def _get_base_dir():
    """Return the project root directory (where config.txt lives).

    When frozen (exe) this is the directory containing the executable.
    When running as a script this is two levels up from this file
    (src/utils/ → project root).
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config(filepath="config.txt"):
    config = {}
    full_path = os.path.join(_get_base_dir(), filepath)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config
