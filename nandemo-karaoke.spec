# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=[],
    # binaries=[('venv/bin/spleeter', '.'),],
    datas=[
        ('src/gui/ui', 'gui/ui'),
        ('venv/lib/python3.10/site-packages/spleeter', 'spleeter'),
        ('venv/lib/python3.10/site-packages/ffmpeg', 'ffmpeg'),
        ('venv/lib/python3.10/site-packages/httpx', 'httpx'),
        ('venv/lib/python3.10/site-packages/norbert', 'norbert'),
        ('venv/lib/python3.10/site-packages/pandas', 'pandas'),
        ('venv/lib/python3.10/site-packages/typer', 'typer'),
        ('venv/lib/python3.10/site-packages/tensorflow', 'tensorflow'),
        ('venv/lib/python3.10/site-packages/whisper/assets','whisper/assets'),
        ('pretrained_models', 'spleeter/pretrained_models'),
    ],
    hiddenimports=['spleeter','whisper','tensorflow'],
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
    [],
    exclude_binaries=True,
    name='nandemo-karaoke',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='nandemo-karaoke',
)