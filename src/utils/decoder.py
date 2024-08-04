# utils/decoder.py

def decode_ascii(data: bytes) -> str:
	"""
	將 ASCII 編碼的資料解碼為可讀格式。

	參數:
	data (bytes): 以 ASCII 編碼的資料。

	返回:
	str: 解碼後的字串（去除最後的空格）。
	"""
	return data.decode('ascii').rstrip()

def decode_packed_bcd(data: bytes) -> str:
	"""
	將 PACK BCD 編碼的資料解碼為整數。

	參數:
	data (bytes): 以 PACK BCD 編碼的資料。

	返回:
	str: 解碼後的數字字串。
	"""
	result = ''
	for byte in data:
		high_nibble = (byte >> 4) & 0xF
		low_nibble = byte & 0xF
		# 將高位和低位轉換為字串
		result += f'{high_nibble}{low_nibble}'

	return result

def decode_hexacode(hexacode: bytes) -> str:
	"""
	將 HEXACODE 編碼的資料轉換為可讀格式。

	參數:
	hexacode (bytes): 以 HEXACODE 表示的字串。

	返回:
	str: 解碼後的字串。
	"""
	return hexacode.hex().upper()
