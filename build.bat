@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building MusicBot.exe...
pyinstaller --onefile --console --name MusicBot ^
    --hidden-import Musiccommand ^
    --hidden-import config_loader ^
    --hidden-import ffmpeg_setup ^
    --hidden-import discord ^
    --hidden-import youtube_dl ^
    --hidden-import aiohttp ^
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
