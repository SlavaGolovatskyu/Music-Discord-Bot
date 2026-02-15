# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[('C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\nacl\\_sodium.pyd', 'nacl')],
    datas=[],
    hiddenimports=['Musiccommand', 'config_loader', 'ffmpeg_setup', 'discord', 'yt_dlp', 'aiohttp', '_cffi_backend', 'nacl', 'nacl._sodium', 'nacl.bindings', 'nacl.bindings.crypto_aead', 'nacl.bindings.crypto_box', 'nacl.bindings.crypto_secretbox', 'nacl.bindings.crypto_sign', 'nacl.bindings.utils', 'nacl.bindings.sodium_core', 'nacl.bindings.randombytes', 'nacl.public', 'nacl.secret', 'nacl.signing', 'nacl.encoding', 'nacl.hash', 'nacl.utils'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MusicBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
