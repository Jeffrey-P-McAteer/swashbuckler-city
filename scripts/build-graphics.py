#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#
# ]
# ///

import pathlib
import os
import sys
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


# TODO better organization
subprocess.run([
  os.path.join(REPO_ROOT, 'scripts', 'build-graphics-fonts.py')
])

