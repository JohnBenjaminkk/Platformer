block_cipher = None

a = Analysis(
    ['Learning2\\game.py'],  # Changed to Windows path
    pathex=['c:\\Pizdec\\Platformer'],  # Added explicit path
    binaries=[],    datas=[
        ('Learning2\\img\\*.png', 'img'),  # Changed to Windows paths
        ('Learning2\\img\\*.wav', 'img'),
        ('level1_data', '.'),
        ('level2_data', '.'),
        ('level3_data', '.'),
        ('level4_data', '.'),
        ('level5_data', '.'),
        ('level6_data', '.'),
        ('level7_data', '.'),
        ('level8_data', '.'),
    ],
    hiddenimports=['pygame'],
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
    name='Platformer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,    console=False,  # Changed to False for release
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Learning2\\img\\coin.png'  # Changed to Windows path
)