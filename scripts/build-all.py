#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "zstandard",
# ]
# ///

import pathlib
import os
import sys
import subprocess
import shutil
import urllib.request
import re
import tarfile
import io
import shlex

import zstandard

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DEBUG = os.environ.get('DEBUG', '').lower() in ('y', '1', 't')

# Clean environment vars
os.environ.pop('RUSTFLAGS', None)

# Ensure build tools are available

required_bins = ['cargo', 'zig']

for b in required_bins:
  if not shutil.which(b):
    print(f'[ Fatal Error] required binary "{b}" does not exist. Install and re-run.')
    sys.exit(1)


if not shutil.which('cargo-zigbuild'):
  yn = input(f'Need cargo-zigbuild[.exe] installed, ok to install?').strip().lower()
  if not (yn[:1] in ('y', '1', 't') ):
    print(f'[ Fatal Error] Cannot install cargo-zigbuild, exiting.')
    sys.exit(1)
  subprocess.run([
    'cargo', 'install', '--locked', 'cargo-zigbuild'
  ], check=True)

# (Assuming exec on linux system)
# We must manually download a copy of the mingw build tools which zig calls out to - https://packages.msys2.org/packages/mingw-w64-cross-mingw64-binutils?variant=x86_64

if not shutil.which('x86_64-w64-mingw32-dlltool'):
  mingw32_tools_folder = os.path.join(pathlib.Path.home(), '.cache', 'mingw32_tools_folder')
  os.makedirs(mingw32_tools_folder, exist_ok=True)
  print(f'x86_64-w64-mingw32-dlltool not found, loading from {mingw32_tools_folder}')
  os.environ['PATH'] = os.pathsep.join([
      os.environ['PATH'],
      mingw32_tools_folder,
      os.path.join(mingw32_tools_folder, 'bin'),
      os.path.join(mingw32_tools_folder, 'usr', 'bin'),
      os.path.join(mingw32_tools_folder, 'opt', 'bin'),
      os.path.join(mingw32_tools_folder, 'opt', 'x86_64-w64-mingw32', 'bin'),
  ])
  if not shutil.which('x86_64-w64-mingw32-dlltool'):
    # with urllib.request.urlopen('https://packages.msys2.org/packages/mingw-w64-cross-mingw64-binutils?variant=x86_64') as response:
    #   html = response.read().decode()
    # matches = re.findall(r'https://[^>]*mingw64.binutils[^>]*.x86_64.pkg.tar.zst', html, flags=re.MULTILINE)
    # first_link = matches[0]
    first_link = 'https://archlinux.org/packages/extra/x86_64/mingw-w64-binutils/download/'
    print(f'Downloading {first_link}')
    with urllib.request.urlopen(first_link) as response:
      zst_data = response.read()
    dctx = zstandard.ZstdDecompressor()
    #decompressed = dctx.decompress(zst_data)
    zst_stream = io.BytesIO(zst_data)
    with dctx.stream_reader(zst_stream) as reader:
      decompressed_tar_data = io.BytesIO(reader.read())
    #tar_buffer = io.BytesIO(decompressed_tar_data)
    with tarfile.open(fileobj=decompressed_tar_data, mode='r:') as tar:
      tar.extractall(path=mingw32_tools_folder)

if DEBUG:
  print('Using downloaded binary', shutil.which('x86_64-w64-mingw32-dlltool'))


# Ensure all generated graphics are up to date
subprocess.run([
  os.path.join(REPO_ROOT, 'scripts', 'build-graphics.py')
])


def find_target_binary(t, bin_base_name):
  canidates = [
    os.path.join('target', t, 'release', f'{bin_base_name}.exe'),
    os.path.join('target', t, 'release', f'{bin_base_name}'),
  ]
  for c in canidates:
    if os.path.exists(c):
      return c
  raise Exception(f'Cannot find a binary for {t}')

def file_size_mb(file_path):
  num_bytes = 0
  try:
    num_bytes = os.path.getsize(file_path)
  except:
    pass
  num_mb = float(num_bytes) / 1_000_000
  return f'{num_mb:.1f}mb'

def print_run(cmd, **subprocess_kwargs):
  debug_cmd = shlex.join(cmd)
  print(f'> {debug_cmd}')
  subprocess.run(cmd, **subprocess_kwargs)

class Build:
  def __init__(self, folder_name, required_targets, optional_targets):
    self.folder_name = folder_name
    self.required_targets = required_targets
    self.optional_targets = optional_targets

  def build(self):
    title_border = '================'
    for required_target in self.required_targets:
      print()
      print(f'{title_border} required: {required_target} {title_border}')
      print_run([
        'cargo', 'zigbuild', '--package', self.folder_name, '--release', '--target', f'{required_target}'
      ], check=True)
      out_bin_path = os.path.abspath(find_target_binary(required_target, self.folder_name))
      print(f'[ Built ] {out_bin_path} ({file_size_mb(out_bin_path)})')

    for optional_target in self.optional_targets:
      print()
      print(f'{title_border} optional: {required_target} {title_border}')
      print_run([
        'cargo', 'zigbuild', '--package', self.folder_name, '--release', '--target', f'{optional_target}'
      ], check=False)
      try:
        out_bin_path = os.path.abspath(find_target_binary(optional_target, self.folder_name))
        print(f'[ Built ] {out_bin_path} ({file_size_mb(out_bin_path)})')
      except:
        print(f'[ Fail ] Failed to compile {self.folder_name} for {optional_target}')


builds = [
  Build('sc-linux',
    required_targets=['x86_64-unknown-linux-gnu'],
    optional_targets=['aarch64-unknown-linux-gnu']
  ),
  Build('sc-macos',
    required_targets=['x86_64-apple-darwin'],
    optional_targets=['aarch64-apple-darwin']
  ),
  Build('sc-windows',
    required_targets=['x86_64-pc-windows-gnu'],
    optional_targets=['aarch64-pc-windows-gnullvm']
  )
]

for b in builds:
  b.build()


