#!/usr/bin/env python3
"""Prove a stamped app is upstream's app: every file matches except the stamp.

Mach-O files are compared without their code signature and the size fields that point at it,\nsince re-signing rewrites only those.
Allowed differences: Info.plist keys the stamp sets, the icon, the update feed's owner and repo,
the removed provisioning profile and signature files. Anything else fails.

usage: compare-bundles.py <upstream.app> <stamped.app>
"""
import hashlib
from pathlib import Path
import plistlib
import struct
import sys

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


FAT_MAGICS = {b'\xca\xfe\xba\xbe': '>', b'\xbe\xba\xfe\xca': '<'}
# Thin magic -> (header size, segment command, offsets of vmsize and filesize, field format)
THIN = {b'\xcf\xfa\xed\xfe': (32, 0x19, 32, 48, 'Q'), b'\xce\xfa\xed\xfe': (28, 0x1, 28, 36, 'I')}
LC_CODE_SIGNATURE = 0x1D


def is_macho(path):
    with path.open('rb') as stream:
        magic = stream.read(4)
    return magic in THIN or magic in FAT_MAGICS


def unsigned_slice(data):
    """A thin Mach-O up to its code signature, with the fields that point at the signature
    zeroed. Re-signing changes only those; every code and data byte stays put."""
    layout = THIN.get(data[:4])
    if layout is None:
        return data
    header, segment, vmsize, filesize, field = layout
    width = struct.calcsize(field)
    out = bytearray(data)
    ncmds = struct.unpack_from('<I', data, 16)[0]
    offset, signature, linkedit = header, None, None
    for _ in range(ncmds):
        cmd, size = struct.unpack_from('<II', data, offset)
        if cmd == LC_CODE_SIGNATURE:
            signature = offset
        elif cmd == segment and data[offset + 8:offset + 24].rstrip(b'\0') == b'__LINKEDIT':
            linkedit = offset
        offset += size
    if signature is None:
        return data
    end = struct.unpack_from('<I', data, signature + 8)[0]
    out[signature + 8:signature + 16] = bytes(8)
    if linkedit is not None:
        out[linkedit + vmsize:linkedit + vmsize + width] = bytes(width)
        out[linkedit + filesize:linkedit + filesize + width] = bytes(width)
    return bytes(out[:end])


def unsigned_slices(path):
    data = path.read_bytes()
    order = FAT_MAGICS.get(data[:4])
    if order is None:
        return [unsigned_slice(data)]
    count = struct.unpack_from(order + 'I', data, 4)[0]
    slices = []
    for index in range(count):
        # Offsets and sizes move when slices are re-signed; architecture and alignment do not.
        cputype, subtype, offset, size, align = struct.unpack_from(order + 'iiIII', data, 8 + 20 * index)
        slices.append((cputype, subtype, align, unsigned_slice(data[offset:offset + size])))
    return slices


def main(upstream, stamped):
    left, right = files(upstream), files(stamped)
    problems = []
    # Only the icon the stamp replaced may differ; any other .icns must match upstream.
    icon_file = plistlib.loads((upstream / 'Contents/Info.plist').read_bytes()).get('CFBundleIconFile', '')
    stamped_icon = f"Contents/Resources/{icon_file.removesuffix('.icns')}.icns" if icon_file else None
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
        if relative == stamped_icon:
            continue
        if digest(a) == digest(b):
            continue
        if is_macho(a) and is_macho(b) and unsigned_slices(a) == unsigned_slices(b):
            continue
        problems.append(f'content differs: {relative}')
    print(f'compared {len(left)} upstream files with {len(right)} stamped files')
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
