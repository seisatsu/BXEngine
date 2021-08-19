# -*- mode: python ; coding: utf-8 -*-


import os

import pygame_gui
pygame_gui_path = os.path.dirname(pygame_gui.__file__).replace('\\', '/')

block_cipher = None


a = Analysis(['bxengine.py'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[('common/*', 'common/'), ('test_world/*', 'test_world/'), (pygame_gui_path + '*', 'pygame_gui/')],
             hiddenimports=['jsonschema'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='bxengine',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
