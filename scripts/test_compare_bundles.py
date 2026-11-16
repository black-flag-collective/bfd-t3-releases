import importlib.util
from pathlib import Path
import struct
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

    def test_note_payload_outside_segments_is_retained(self):
        data = bytearray(272)
        data[:4] = b'\xcf\xfa\xed\xfe'
        struct.pack_into('<II', data, 16, 2, 56)
        struct.pack_into('<II16sQQ', data, 32, 0x31, 40, b'owner', 200, 4)
        struct.pack_into('<IIII', data, 72, 0x1d, 16, 256, 16)
        self.assertEqual(len(compare.unsigned_slice(bytes(data))), 204)
        changed = bytearray(data)
        changed[201] = 1
        self.assertNotEqual(compare.unsigned_slice(bytes(data)), compare.unsigned_slice(bytes(changed)))


if __name__ == '__main__':
    unittest.main()
