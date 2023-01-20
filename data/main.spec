# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['C:/Users/Zver/PycharmProjects/Tanks_project'],
    binaries=[],
    datas=[('data/level.txt', 'data'), ('data/booms.png', 'data'), ('data/crown.png', 'data'), ('data/fire.png', 'data'), ('data/flor.png', 'data'), ('data/fon.png', 'data'), ('data/grass.png', 'data'), ('data/green_bullet.png', 'data'), ('data/green_tank.png', 'data'), ('data/spawn.png', 'data'), ('data/unbreakable_wall.png', 'data'), ('data/wall.png', 'data'), ('data/wall_1.png', 'data'), ('data/wall_2.png', 'data'), ('data/wall_3.png', 'data'), ('data/wall_4.png', 'data'), ('data/wall_5.png', 'data'), ('data/wall_6.png', 'data'), ('data/water.png', 'data'), ('data/white_bullet.png', 'data'), ('data/white_tank.png', 'data'), ('data/yellow_bullet.png', 'data'), ('data/yellow_tank.png', 'data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tanks',
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
