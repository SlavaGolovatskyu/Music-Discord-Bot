@echo off
echo Installing dependencies...
pip install pyinstaller PyNaCl discord.py[voice] yt-dlp aiohttp

echo.
echo Locating PyNaCl native binary (_sodium.pyd)...
for /f "delims=" %%i in ('python -c "import nacl, os; print(os.path.join(os.path.dirname(nacl.__file__), '_sodium.pyd'))"') do set SODIUM_PYD=%%i
if not exist "%SODIUM_PYD%" (
    echo ERROR: Could not find _sodium.pyd - PyNaCl may not be installed correctly.
    pause
    exit /b 1
)
echo Found: %SODIUM_PYD%

echo.
echo Building MusicBot.exe...
pyinstaller --onefile --console --clean --name MusicBot ^
    --hidden-import Musiccommand ^
    --hidden-import config_loader ^
    --hidden-import ffmpeg_setup ^
    --hidden-import discord ^
    --hidden-import yt_dlp ^
    --hidden-import aiohttp ^
    --hidden-import _cffi_backend ^
    --hidden-import nacl ^
    --hidden-import nacl._sodium ^
    --hidden-import nacl.bindings ^
    --hidden-import nacl.bindings.crypto_aead ^
    --hidden-import nacl.bindings.crypto_box ^
    --hidden-import nacl.bindings.crypto_secretbox ^
    --hidden-import nacl.bindings.crypto_sign ^
    --hidden-import nacl.bindings.utils ^
    --hidden-import nacl.bindings.sodium_core ^
    --hidden-import nacl.bindings.randombytes ^
    --hidden-import nacl.public ^
    --hidden-import nacl.secret ^
    --hidden-import nacl.signing ^
    --hidden-import nacl.encoding ^
    --hidden-import nacl.hash ^
    --hidden-import nacl.utils ^
    --add-binary "%SODIUM_PYD%;nacl" ^
    Main.py

echo.
echo Copying config.txt to dist folder...
copy config.txt dist\config.txt

echo.
echo ============================================
echo  Build complete!
echo  Your exe is in the "dist" folder.
echo  Make sure config.txt is next to MusicBot.exe
echo  FFmpeg will be downloaded automatically on
echo  first run if not already installed.
echo ============================================
pause
