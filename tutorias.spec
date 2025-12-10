# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('asesorias.db', '.'),
        ('conocimiento_cuatrimestres.md', '.'),
        ('tablas.sql', '.'),
    ],
    hiddenimports=[
        'flask',
        'reportlab',
        'pandas',
        'sqlite3',
        'pdf_generator',
        'academic_history',
        'risk_assessment',
        'utils',
        'datos_inicio',
        'reportlab.pdfbase',
        'reportlab.pdfbase.ttfonts',
        'reportlab.lib.colors',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'pandas._libs.tslibs.timedeltas',
    ],
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
    name='TUTORIAS',
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
    icon=None,
)
