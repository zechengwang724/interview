# utils/format_converter.py

from typing import List, Dict, Any
from .decoder import decode_packed_bcd


def format_number_string(number_str: str, integer_digits: int = None, decimal_digits: int = 0) -> str:
	"""
	將數字字串格式化為整數和小數位數指定的格式，並去掉最前面和最後面的 0。

	參數:
	number_str (str): 原始數字字串。
	integer_digits (int, optional): 整數位。若為 None 則自動計算整數位數。
	decimal_digits (int): 小數位。若為 0 則只顯示整數部分。

	返回:
	str: 格式化後的數字字串，不含最前面與最後面的 0。
	"""
	total_digits = len(number_str)
	
	if decimal_digits == 0:
		# 處理只有整數部分的情況
		integer_part = number_str[-integer_digits:] if integer_digits else number_str
		return integer_part.lstrip('0') or '0'
	
	# 確保數字字串長度足夠
	if integer_digits is None:
		integer_digits = total_digits - decimal_digits
	if total_digits < integer_digits + decimal_digits:
		raise ValueError("數字字串長度不足以包含指定的整數位數和小數位數")

	# 分割整數和小數部分
	integer_part = number_str[-(integer_digits + decimal_digits):-decimal_digits]
	decimal_part = number_str[-decimal_digits:]

	# 去掉整數位最前面的 0 和小數位最後面的 0
	integer_part = integer_part.lstrip('0')
	decimal_part = decimal_part.rstrip('0')

	# 如果小數位全是 0，則不顯示小數點
	if not decimal_part:
		return integer_part if integer_part else '0'
	return f'{integer_part}.{decimal_part}'




def convert_match_time(packed_bcd_data: bytes) -> str:
	"""
	將 PACK BCD 編碼的撮合時間轉換為標準時間格式。

	參數:
	packed_bcd_data (bytes): 以 PACK BCD 編碼的撮合時間資料。

	返回:
	str: 轉換後的時間字串，格式為 "HH:MM:SS.mmmuuu" （時:分:秒:3位毫秒與3位微秒）。
	"""
	# 解碼為數字字串
	decoded_time = decode_packed_bcd(packed_bcd_data)
	
	# 提出時、分、秒、毫秒、微秒
	hours = decoded_time[0:2]
	minutes = decoded_time[2:4]
	seconds = decoded_time[4:6]
	milliseconds = decoded_time[6:9]
	microseconds = decoded_time[9:12]

	# 格式化時間字串
	formatted_time = f"{hours}:{minutes}:{seconds}.{milliseconds}{microseconds}"
	
	return formatted_time


def convert_reveal_flags(binary_data: bytes) -> dict:
	"""
	將揭示項目註記的二進位資料解碼為dict。

	參數:
	binary_data (bytes): 以二進位表示的揭示項目註記。

	返回:
	dict: 解碼後的揭示項目註記。
	"""

	# 確保 binary_data 是單字節的資料
	if len(binary_data) != 1:
		raise ValueError("揭示項目註記應為長度為 1 的 bytes。")

	byte = binary_data[0]
	
	# 提取每一個 Bit 位
	reveal_flags = {
		'成交價成交量': bool(byte & 0b10000000),  # Bit 7
		'買進價買進量': (byte >> 4) & 0b00000111,  # Bit 6-4
		'賣出價賣出量': (byte >> 1) & 0b00000111,  # Bit 3-1
		'僅記成交價量': bool(byte & 0b00000001)    # Bit 0
	}
	
	return reveal_flags


def convert_limit_flags(byte_data: bytes) -> dict:
	"""
	將漲跌停註記的二進位資料解碼為dict。
	
	參數:
	binary_data (bytes): 以二進位表示的漲跌停註記。

	返回:
	dict: 包含每一項漲跌停註記的描述。
	"""

	# 確保 binary_data 是單字節的資料
	if len(byte_data) != 1:
		raise ValueError("漲跌停註記應為長度為 1 的 bytes。")
	
	# 將 bytes 轉換為整數
	byte = byte_data[0]

	# 成交漲跌停註記
	limit_flags = {
		0b00: '一般成交',
		0b01: '跌停成交',
		0b10: '漲停成交'
	}.get((byte >> 6) & 0b11, '未知')
	
	# 最佳一檔買進
	best_bid = {
		0b00: '一般買進',
		0b01: '跌停買進',
		0b10: '漲停買進'
	}.get((byte >> 4) & 0b11, '未知')
	
	# 最佳一檔賣出
	best_ask = {
		0b00: '一般賣出',
		0b01: '跌停賣出',
		0b10: '漲停賣出'
	}.get((byte >> 2) & 0b11, '未知')
	
	# 瞬間價格趨勢
	price_trend = {
		0b00: '一般揭示',
		0b01: '暫緩撮合且瞬間趨跌',
		0b10: '暫緩撮合且瞬間趨漲'
	}.get(byte & 0b11, '保留')
	
	return {
		'成交漲跌停註記': limit_flags,
		'最佳一檔買進': best_bid,
		'最佳一檔賣出': best_ask,
		'瞬間價格趨勢': price_trend
	}

def convert_status_flags(byte_data: bytes) -> dict:
	"""
	將狀態註記的二進位資料解碼為 dict。
	
	參數:
	byte_data (bytes): 以二進位表示的狀態註記。

	返回:
	dict: 包含每一項狀態註記的描述。
	"""

	# 確保 byte_data 是單字節的資料
	if len(byte_data) != 1:
		raise ValueError("狀態註記應為長度為 1 的 bytes。")
	
	# 將 bytes 轉換為整數
	byte = byte_data[0]

	# 試算狀態註記
	trial_status = '試算揭示' if (byte & 0b10000000) else '一般揭示'

	# 如果不是試算揭示，Bit 6 和 Bit 5 的註記無意義
	if byte & 0b10000000 == 0:
		# 試算後延後開盤註記
		post_trial_open = '無意義'
		# 試算後延後收盤註記
		post_trial_close = '無意義'
	else:
		# 試算後延後開盤註記
		post_trial_open = '是' if (byte & 0b01000000) else '否'
		# 試算後延後收盤註記
		post_trial_close = '是' if (byte & 0b00100000) else '否'

	# 撮合方式註記
	matching_method = '逐筆撮合' if (byte & 0b00010000) else '集合競價'
	# 開盤註記
	open_status = '是' if (byte & 0b00001000) else '否'
	# 收盤註記
	close_status = '是' if (byte & 0b00000100) else '否'

	return {
		'試算狀態註記': trial_status,
		'試算後延後開盤註記': post_trial_open,
		'試算後延後收盤註記': post_trial_close,
		'撮合方式註記': matching_method,
		'開盤註記': open_status,
		'收盤註記': close_status
	}


def convert_instant_quotes(prices: List[bytes], quantities: List[bytes], reveal_flags: dict, limit_flags: dict, status_flags: dict, stock_code: str) -> dict:
	"""
	將即時行情的價格和數量資料轉換為可讀格式。

	參數:
	prices (list): 價格欄位的資料，每個元素為 bytes。
	quantities (list): 數量欄位的資料，每個元素為 bytes。
	reveal_flags (dict): 項目註記。
	limit_flags (dict): 漲跌停註記。
	status_flags (dict): 狀態註記。
	stock_code (str): 股票代碼。

	返回:
	dict: 包含轉換後的即時行情資料。
	"""
	result = {
		'成交價量': None,
		'最佳五檔買進價量': [],
		'最佳五檔賣出價量': []
	}

	# 解析註記
	reveal_flag = reveal_flags
	limit_flag = limit_flags
	trial_status = status_flags['試算狀態註記']

	# 檢查是否為中央登錄公債
	is_central_bond = stock_code[0] in ('A', 'C', 'D')

	# 若狀態註記的「試算狀態」為試算揭示
	if trial_status == '試算揭示':
		result['成交價量'] = None
		return result

	# 定義格式化函數
	def format_values(price_bytes: bytes, quantity_bytes: bytes) -> dict:
		return {
			'price': format_number_string(decode_packed_bcd(price_bytes), integer_digits=5, decimal_digits=4),
			'quantity': format_number_string(decode_packed_bcd(quantity_bytes), decimal_digits=0)
		}

	# 判斷 1：是否紀錄成交價量（Bit 7）
	if reveal_flag['成交價成交量']:
		# 解析成交價量
		if limit_flag['瞬間價格趨勢'] == '一般揭示':
			result['成交價量'] = format_values(prices[0], quantities[0])
		else:  # '暫緩撮合' 或 '市價'
			result['成交價量'] = {
				'price': format_number_string(decode_packed_bcd(prices[0]), integer_digits=5, decimal_digits=4),
				'quantity': '0'  # 成交量以 0 揭示
			}
		start_index = 1  # 成交價量佔用 index 0，買進價量從 index 1 開始
	else:
		start_index = 0  # 如果不揭示成交價量，則從 index 0 開始

	# 判斷 2：是否僅揭示成交價量（Bit 0）
	if reveal_flag['僅記成交價量']:
		# 僅揭示成交價量、不揭示最佳五檔買賣價量
		result['最佳五檔買進價量'] = []
		result['最佳五檔賣出價量'] = []
	else:
		# 解析最佳五檔買進價量
		if reveal_flag['買進價買進量'] > 0:
			for i in range(reveal_flag['買進價買進量']):
				index = start_index + i
				if index < len(prices):
					result['最佳五檔買進價量'].append(format_values(prices[index], quantities[index]))
					if is_central_bond:
						break  # 中央登錄公債，只揭示一檔資料

		# 解析最佳五檔賣出價量
		if reveal_flag['賣出價賣出量'] > 0:
			start_index = start_index + reveal_flag['買進價買進量']  # 跳過買進價量的部分
			for i in range(reveal_flag['賣出價賣出量']):
				index = start_index + i
				if index < len(prices):
					result['最佳五檔賣出價量'].append(format_values(prices[index], quantities[index]))
					if is_central_bond:
						break  # 中央登錄公債，只揭示一檔資料

	return result



def calculate_checksum(data: bytes) -> int:
	"""
	計算數據記錄的 XOR 檢查碼。

	參數:
	data (bytes): 需要計算檢查碼的部分。

	返回:
	int: 計算出的 XOR 檢查碼。
	"""
	checksum = 0
	for byte in data:
		checksum ^= byte
	return checksum


