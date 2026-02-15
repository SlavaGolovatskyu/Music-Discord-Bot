import os
import sys
import shutil
import zipfile
import urllib.request
from src.utils.config_loader import load_config

_DEFAULT_FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
_config = load_config()
FFMPEG_URL = _config.get("FFMPEG_URL", _DEFAULT_FFMPEG_URL)


def _get_base_dir():
    """Return the project root directory.

    When frozen (exe) this is the directory containing the executable.
    When running as a script this is two levels up from this file.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _ffmpeg_local_path():
    return os.path.join(_get_base_dir(), "ffmpeg.exe")


def is_ffmpeg_available():
    """Check if ffmpeg exists next to the bot or in system PATH."""
    if os.path.isfile(_ffmpeg_local_path()):
        return True
    return shutil.which("ffmpeg") is not None


def _download_ffmpeg():
    base = _get_base_dir()
    zip_path = os.path.join(base, "ffmpeg.zip")

    print("FFmpeg not found. Downloading (~80 MB), please wait...")
    urllib.request.urlretrieve(FFMPEG_URL, zip_path, _progress_hook)
    print()  # newline after progress

    print("Extracting ffmpeg...")
    needed = ("ffmpeg.exe", "ffprobe.exe")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for entry in zf.namelist():
            filename = os.path.basename(entry)
            if filename in needed:
                dest = os.path.join(base, filename)
                with zf.open(entry) as src, open(dest, "wb") as dst:
                    dst.write(src.read())

    os.remove(zip_path)
    print("FFmpeg installed successfully!")


def _progress_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(downloaded * 100 / total_size, 100)
        print(f"\r  Downloading: {percent:.0f}%", end="", flush=True)


def ensure_ffmpeg():
    """Make sure ffmpeg is available. Downloads it if missing."""
    if is_ffmpeg_available():
        return

    try:
        _download_ffmpeg()
    except Exception as e:
        print(f"ERROR: Failed to download FFmpeg: {e}")
        print("Please install FFmpeg manually and place ffmpeg.exe next to the bot.")
        sys.exit(1)

    # Add the bot directory to PATH so discord.py can find ffmpeg
    base = _get_base_dir()
    if base not in os.environ.get("PATH", ""):
        os.environ["PATH"] = base + os.pathsep + os.environ.get("PATH", "")
