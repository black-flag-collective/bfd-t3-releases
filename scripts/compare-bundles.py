#!/usr/bin/env python3
"""Prove a stamped app is upstream's app: every file matches except the stamp.

Mach-O files are compared with their code signatures removed, since re-signing rewrites them.
Allowed differences: Info.plist keys the stamp sets, the icon, the update feed's owner and repo,
the removed provisioning profile and signature files. Anything else fails.

usage: compare-bundles.py <upstream.app> <stamped.app>
"""
import hashlib
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile

STAMPED_PLIST_KEYS = {'CFBundleName', 'CFBundleDisplayName', 'ElectronTeamID', 'CFBundleIconName'}


def files(root):
    found = {}
    for path in root.rglob('*'):
        if path.is_file() and not path.is_symlink():
            relative = path.relative_to(root).as_posix()
            if '/_CodeSignature/' not in f'/{relative}' and not relative.endswith('/CodeResources'):
                found[relative] = path
    return found


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_macho(path):
    with path.open('rb') as stream:
        magic = stream.read(4)
    return magic in (b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca')


def unsigned_digest(path, scratch):
    copy = Path(scratch) / 'binary'
    shutil.copyfile(path, copy)
    os.chmod(copy, 0o755)
    subprocess.run(['codesign', '--remove-signature', str(copy)], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return digest(copy)


def main(upstream, stamped):
    left, right = files(upstream), files(stamped)
    problems = []
    for relative in sorted(set(left) | set(right)):
        if relative == 'Contents/embedded.provisionprofile' and relative not in right:
            continue
        if relative not in left or relative not in right:
            problems.append(f'only in {"upstream" if relative in left else "stamped"}: {relative}')
            continue
        a, b = left[relative], right[relative]
        if relative == 'Contents/Info.plist':
            pa, pb = plistlib.loads(a.read_bytes()), plistlib.loads(b.read_bytes())
            changed = {k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k)}
            if changed - STAMPED_PLIST_KEYS:
                problems.append(f'Info.plist keys changed: {sorted(changed - STAMPED_PLIST_KEYS)}')
            continue
        if relative == 'Contents/Resources/app-update.yml':
            strip = lambda text: [line for line in text.splitlines()
                                  if not line.startswith(('owner:', 'repo:'))]
            if strip(a.read_text()) != strip(b.read_text()):
                problems.append('app-update.yml changed beyond owner and repo')
            continue
        if relative.startswith('Contents/Resources/') and relative.endswith('.icns'):
            continue
        if digest(a) == digest(b):
            continue
        if is_macho(a) and is_macho(b):
            with tempfile.TemporaryDirectory() as scratch:
                if unsigned_digest(a, scratch) == unsigned_digest(b, scratch):
                    continue
        problems.append(f'content differs: {relative}')
    print(f'compared {len(left)} upstream files with {len(right)} stamped files')
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
