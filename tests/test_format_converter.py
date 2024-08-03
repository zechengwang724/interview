import unittest
from src.utils.format_converter import (
	format_number_string,
	convert_match_time,
	convert_reveal_flags,
	convert_limit_flags,
	convert_instant_quotes,
	calculate_checksum
)

class TestFormatConverter(unittest.TestCase):

	# 測試數字轉換
	def test_format_with_integer_and_decimal(self):
		self.assertEqual(format_number_string('0000236500', integer_digits=5, decimal_digits=4), '23.65')
	
	def test_format_with_only_integer(self):
		self.assertEqual(format_number_string('0000234500', decimal_digits=0), '234500')
	
	def test_format_with_all_zeroes(self):
		self.assertEqual(format_number_string('0000000000', integer_digits=5, decimal_digits=4), '0')
	

	def test_convert_match_time(self):
		# 測試 PACK BCD 編碼的撮合時間轉換
		packed_bcd_data = bytes([0x12, 0x34, 0x56, 0x78, 0x12, 0x34])
		expected = '12:34:56.781234'
		result = convert_match_time(packed_bcd_data)
		self.assertEqual(result, expected)

	def test_convert_reveal_flags(self):
		# 測試揭示項目註記的二進位資料解碼
		binary_data = bytes([0b10000000])
		expected = {
			'成交價成交量': True,
			'買進價買進量': 0,
			'賣出價賣出量': 0,
			'僅記成交價量': False
		}
		result = convert_reveal_flags(binary_data)
		self.assertEqual(result, expected)

	def test_convert_limit_flags(self):
		# 測試漲跌停註記的二進位資料解碼
		byte_data = bytes([0b00000001])
		expected = {
			'成交漲跌停註記': '一般成交',
			'最佳一檔買進': '一般買進',
			'最佳一檔賣出': '一般賣出',
			'瞬間價格趨勢': '暫緩撮合且瞬間趨跌'
		}
		result = convert_limit_flags(byte_data)
		self.assertEqual(result, expected)

	def test_convert_instant_quotes(self):
		# 測試即時行情的價格和數量資料轉換
		prices = [
			bytes([0x00, 0x00, 0x12, 0x34, 0x00]),  # 成交價
			bytes([0x00, 0x00, 0x56, 0x78, 0x00]),  # 最佳五檔買進價
			bytes([0x00, 0x00, 0x12, 0x34, 0x00])   # 最佳五檔賣出價
		]
		quantities = [
			bytes([0x00, 0x00, 0x12, 0x12]),  # 成交量
			bytes([0x00, 0x00, 0x23, 0x23]),  # 最佳五檔買進量
			bytes([0x00, 0x00, 0x34, 0x34])   # 最佳五檔賣出量
		]
		reveal_flags = {
			'成交價成交量': True,
			'買進價買進量': 1,
			'賣出價賣出量': 1,
			'僅記成交價量': False,
		}
		limit_flags = {
			'成交漲跌停註記': '一般成交',
			'最佳一檔買進': '一般買進',
			'最佳一檔賣出': '一般賣出',
			'瞬間價格趨勢': '一般揭示'
		}
		status_flags = {
			'試算狀態註記': '一般揭示',
			'試算後延後開盤註記': '無意義',
			'試算後延後收盤註記': '無意義',
			'撮合方式註記': '集合競價',
			'開盤註記': '否',
			'收盤註記': '否'
		}
		stock_code = '1101'
		expected = {
			'成交價量': {
				'price': '12.34',
				'quantity': '1212'
			},
			'最佳五檔買進價量': [
				{'price': '56.78', 'quantity': '2323'}
			],
			'最佳五檔賣出價量': [
				{'price': '12.34', 'quantity': '3434'}
			]
		}
		result = convert_instant_quotes(prices, quantities, reveal_flags, limit_flags, status_flags, stock_code)
		self.assertEqual(result, expected)

	def test_calculate_checksum(self):
		# 測試 XOR 檢查碼計算
		data = bytes([0x01, 0x02, 0x03])
		expected = 0x00  # 1 ^ 2 ^ 3 = 0
		result = calculate_checksum(data)
		self.assertEqual(result, expected)

if __name__ == '__main__':
	unittest.main()