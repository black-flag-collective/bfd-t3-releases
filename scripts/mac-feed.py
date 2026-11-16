#!/usr/bin/env python3
"""Write electron-updater's nightly-mac.yml for the stamped zips and dmgs in a folder.

usage: mac-feed.py <version> <dir>
"""
import base64
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys

version, folder = sys.argv[1], Path(sys.argv[2])
entries = []
for path in sorted(folder.iterdir()):
    if path.suffix in ('.zip', '.dmg') and version in path.name:
        sha512 = base64.b64encode(hashlib.sha512(path.read_bytes()).digest()).decode()
        entries.append((path.name, sha512, path.stat().st_size))
zips = [entry for entry in entries if entry[0].endswith('.zip')]
if not zips:
    sys.exit('no zips to publish')
lines = [f"version: '{version}'", 'files:']
for name, sha512, size in entries:
    lines += [f'  - url: {name}', f'    sha512: {sha512}', f'    size: {size}']
# Like upstream's feed: electron-updater picks each Mac's zip from `files` by architecture.
lines += [f"releaseDate: '{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')}'"]
(folder / 'nightly-mac.yml').write_text('\n'.join(lines) + '\n')
print((folder / 'nightly-mac.yml').read_text())
