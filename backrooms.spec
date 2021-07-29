# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['backrooms.py'],
             pathex=['C:\\Users\\user\\Documents\\Share\\Backrooms'],
             binaries=[],
             datas=[('images/*', 'images/'), ('test_world/*', 'test_world/'), ('c:/users/user/appdata/local/programs/python/python39/lib/site-packages/pygame_gui*', 'pygame_gui/')],
             hiddenimports=[],
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
          name='backrooms',
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
