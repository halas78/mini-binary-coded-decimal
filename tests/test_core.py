import unittest

from mini_binary_coded_decimal import (
    decode_packed,
    decode_unpacked,
    encode_packed,
    encode_unpacked,
)


class TestEncodePacked(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode_packed(0), b"\x00")

    def test_single_digit_pads_to_byte(self):
        self.assertEqual(encode_packed(5), b"\x05")

    def test_two_digits(self):
        self.assertEqual(encode_packed(42), b"\x42")

    def test_implicit_padding_odd(self):
        # 3 digits -> padded to 4 nibbles = 2 bytes
        self.assertEqual(encode_packed(123), b"\x01\x23")

    def test_explicit_digits_odd(self):
        self.assertEqual(encode_packed(7, digits=3), b"\x00\x07")

    def test_explicit_digits_even(self):
        self.assertEqual(encode_packed(7, digits=4), b"\x00\x07")

    def test_digits_must_fit(self):
        with self.assertRaises(ValueError):
            encode_packed(999, digits=2)

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            encode_packed(-1)


class TestDecodePacked(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(decode_packed(b"\x00"), 0)

    def test_roundtrip(self):
        for n in (0, 1, 9, 10, 99, 100, 12345):
            self.assertEqual(decode_packed(encode_packed(n)), n)

    def test_leading_pad_nibble_allowed(self):
        self.assertEqual(decode_packed(b"\x05"), 5)

    def test_invalid_high_nibble(self):
        with self.assertRaises(ValueError):
            decode_packed(b"\xF0")

    def test_invalid_low_nibble(self):
        with self.assertRaises(ValueError):
            decode_packed(b"\x0F")

    def test_type_error(self):
        with self.assertRaises(TypeError):
            decode_packed("05")


class TestEncodeUnpacked(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode_unpacked(0), b"\x00")

    def test_single_digit(self):
        self.assertEqual(encode_unpacked(7), b"\x07")

    def test_multi_digit(self):
        self.assertEqual(encode_unpacked(42), b"\x04\x02")

    def test_padding(self):
        self.assertEqual(encode_unpacked(42, digits=4), b"\x00\x00\x04\x02")

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            encode_unpacked(-1)


class TestDecodeUnpacked(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(decode_unpacked(b"\x00"), 0)

    def test_roundtrip(self):
        for n in (0, 1, 9, 10, 99, 100, 12345):
            self.assertEqual(decode_unpacked(encode_unpacked(n)), n)

    def test_rejects_non_zero_high_nibble(self):
        # 0x34 has a non-zero high nibble -> not valid unpacked BCD
        with self.assertRaises(ValueError):
            decode_unpacked(b"\x34")

    def test_rejects_invalid_low_nibble(self):
        with self.assertRaises(ValueError):
            decode_unpacked(b"\x0A")

    def test_type_error(self):
        with self.assertRaises(TypeError):
            decode_unpacked("00")


if __name__ == "__main__":
    unittest.main()
