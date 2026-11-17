import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('compare_bundles', Path(__file__).with_name('compare-bundles.py'))
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


def binary(signature_offset=128, payload=b'code\0', signature=b'signature'):
    data = bytearray(signature_offset + len(signature))
    data[:4] = b'\xcf\xfa\xed\xfe'
    struct.pack_into('<II', data, 16, 2, 40)
    struct.pack_into('<IIIIII', data, 32, 2, 24, 0, 0, 80, len(payload))
    struct.pack_into('<IIII', data, 56, 0x1d, 16, signature_offset, len(signature))
    data[80:80 + len(payload)] = payload
    data[signature_offset:] = signature
    return bytes(data)


class SignatureComparisonTests(unittest.TestCase):
    def test_moved_signature_ignores_only_unreferenced_zero_padding(self):
        original = binary()
        moved = binary(144, signature=b'resigned')
        self.assertEqual(compare.unsigned_slice(original), compare.unsigned_slice(moved))
        self.assertNotEqual(compare.unsigned_slice(original), compare.unsigned_slice(binary(144, b'codE\0')))
        self.assertNotEqual(compare.unsigned_slice(original), compare.unsigned_slice(binary(144, b'code')))
        changed_padding = bytearray(moved)
        changed_padding[100] = 1
        self.assertNotEqual(compare.unsigned_slice(original), compare.unsigned_slice(bytes(changed_padding)))


    def test_trailing_bytes_after_signature_are_compared(self):
        original = binary()
        self.assertNotEqual(compare.unsigned_slice(original), compare.unsigned_slice(original + b'changed'))
        self.assertNotEqual(compare.unsigned_slice(original), compare.unsigned_slice(original + bytes(16)))

    def test_dysymtab_module_sizes_and_segment_field_widths(self):
        for header, segment_size, segment_cmd, field, module_size in (
                (32, 72, 0x19, 'Q', 56), (28, 56, 1, 'I', 52)):
            with self.subTest(header=header):
                data = bytearray(336)
                data[:4] = b'\xcf\xfa\xed\xfe' if header == 32 else b'\xce\xfa\xed\xfe'
                struct.pack_into('<II', data, 16, 3, segment_size + 96)
                struct.pack_into('<II16s', data, header, segment_cmd, segment_size, b'__LINKEDIT')
                fileoff = header + (40 if header == 32 else 32)
                struct.pack_into('<' + field, data, fileoff, 224)
                dysymtab = header + segment_size
                struct.pack_into('<II', data, dysymtab, 0xb, 80)
                struct.pack_into('<II', data, dysymtab + 40, 224, 1)
                struct.pack_into('<IIII', data, dysymtab + 80, 0x1d, 16, 320, 16)
                normalized = compare.unsigned_slice(bytes(data))
                self.assertEqual(len(normalized), 224 + module_size)
                self.assertEqual(struct.unpack_from('<' + field, normalized, fileoff)[0], 224)

    def test_big_endian_slices_normalize_signature_changes(self):
        for header, magic in ((28, b'\xfe\xed\xfa\xce'), (32, b'\xfe\xed\xfa\xcf')):
            with self.subTest(header=header):
                data = bytearray(144)
                data[:4] = magic
                struct.pack_into('>II', data, 16, 2, 40)
                struct.pack_into('>IIIIII', data, header, 2, 24, 0, 0, 96, 4)
                struct.pack_into('>IIII', data, header + 24, 0x1d, 16, 128, 16)
                data[96:100] = b'code'
                changed = bytearray(data)
                changed[128:] = b'x' * 16
                self.assertEqual(compare.unsigned_slice(bytes(data)), compare.unsigned_slice(bytes(changed)))
                changed[96] = 1
                self.assertNotEqual(compare.unsigned_slice(bytes(data)), compare.unsigned_slice(bytes(changed)))

    def test_fat_metadata_and_padding_are_not_discarded(self):
        def fat(second_offset=256, first=None):
            first = first or binary()
            second = binary()
            data = bytearray(second_offset + len(second))
            struct.pack_into('>II', data, 0, 0xcafebabe, 2)
            struct.pack_into('>iiIII', data, 8, 7, 3, 64, len(first), 4)
            struct.pack_into('>iiIII', data, 28, 12, 0, second_offset, len(second), 4)
            data[64:64 + len(first)] = first
            data[second_offset:] = second
            return bytes(data)
        def normalized(data):
            with tempfile.TemporaryDirectory() as root:
                path = Path(root) / 'fat'
                path.write_bytes(data)
                return compare.unsigned_slices(path)
        original = fat()
        self.assertEqual(normalized(original), normalized(fat(272, binary(144, signature=b'resigned'))))
        for position in (50, 220, 24):
            changed = bytearray(original)
            changed[position] ^= 1
            self.assertNotEqual(normalized(original), normalized(bytes(changed)))

    def test_fat64_slices_and_reserved_metadata(self):
        for order, magic in (('>', b'\xca\xfe\xba\xbf'), ('<', b'\xbf\xba\xfe\xca')):
            with self.subTest(order=order), tempfile.TemporaryDirectory() as root:
                def normalized(signature, reserved=0):
                    thin = binary(signature=signature)
                    data = bytearray(64 + len(thin))
                    data[:4] = magic
                    struct.pack_into(order + 'IiiQQII', data, 4, 1, 7, 3, 64, len(thin), 4, reserved)
                    data[64:] = thin
                    path = Path(root) / 'fat64'
                    path.write_bytes(data)
                    self.assertTrue(compare.is_macho(path))
                    return compare.unsigned_slices(path)
                self.assertEqual(normalized(b'original'), normalized(b'resigned'))
                self.assertNotEqual(normalized(b'original'), normalized(b'original', 1))

    def test_malformed_magic_prefixed_files_compare_as_raw_bytes(self):
        cases = [b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe']
        invalid_command = bytearray(binary())
        struct.pack_into('<I', invalid_command, 36, 0)
        cases.append(bytes(invalid_command))
        for data in cases:
            with self.subTest(data=data[:4]), tempfile.TemporaryDirectory() as root:
                path = Path(root) / 'malformed'
                path.write_bytes(data)
                self.assertEqual(compare.unsigned_slices(path), [data])

    def test_note_and_symseg_payloads_outside_segments_are_retained(self):
        for cmd, size in ((0x31, 40), (0x3, 16)):
            with self.subTest(command=cmd):
                data = bytearray(272)
                data[:4] = b'\xcf\xfa\xed\xfe'
                struct.pack_into('<II', data, 16, 2, size + 16)
                if cmd == 0x31:
                    struct.pack_into('<II16sQQ', data, 32, cmd, size, b'owner', 200, 4)
                else:
                    struct.pack_into('<IIII', data, 32, cmd, size, 200, 4)
                struct.pack_into('<IIII', data, 32 + size, 0x1d, 16, 256, 16)
                self.assertEqual(len(compare.unsigned_slice(bytes(data))), 204)
                data[200:204] = b'data'
                resigned = bytearray(data)
                resigned[256:] = b'x' * 16
                self.assertEqual(compare.unsigned_slice(bytes(data)), compare.unsigned_slice(bytes(resigned)))
                changed = bytearray(data)
                changed[201] = 1
                self.assertNotEqual(compare.unsigned_slice(bytes(data)), compare.unsigned_slice(bytes(changed)))


if __name__ == '__main__':
    unittest.main()
