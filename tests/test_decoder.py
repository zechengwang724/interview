# tests/test_decoder.py

import unittest
from src.utils.decoder import decode_ascii, decode_packed_bcd, decode_hexacode

class TestDecoder(unittest.TestCase):

	def test_decode_ascii(self):
		# 測試 ASCII 編碼解碼
		data = b'hello'
		expected = 'hello'
		result = decode_ascii(data)
		self.assertEqual(result, expected)

	def test_decode_packed_bcd(self):
		# 測試 PACK BCD 編碼解碼
		data = bytes([0x12, 0x34, 0x56, 0x78, 0x12, 0x34])
		expected = "123456781234"
		result = decode_packed_bcd(data)
		self.assertEqual(result, expected)

	def test_decode_hexacode(self):
		# 測試 HEXACODE 編碼解碼
		hexacode = b'\x12\x34\x56\x78'
		expected = '12345678'
		result = decode_hexacode(hexacode)
		self.assertEqual(result, expected)

if __name__ == '__main__':
	unittest.main()