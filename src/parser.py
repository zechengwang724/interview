# src/parser.py
# from utils.header.header_parser import parse_header
# from utils.body.body_parser import parse_body

from typing import List, Dict, Any, Tuple, Union
from constants import ESC_CODE, TERMINAL_CODE
from utils.decoder import decode_ascii, decode_packed_bcd, decode_hexacode
from utils.format_converter import format_number_string, convert_match_time, convert_reveal_flags, convert_limit_flags, convert_status_flags, convert_instant_quotes, calculate_checksum


def parse_file(file_path: str, skip_conditions: List[Dict[str, Union[int, Tuple[int, int], str]]] = None) -> List[Dict[str, Any]]:
	"""
	解析二進位數據文件，提取並處理每筆記錄。

	參數:
	file_path(str): 解析的數據文件的路徑。
	skip_conditions(list): 包含多個條件的列表，每個條件是包含位置、指定數值和模式的 dict。

	輸出:
	list: 包含解析後的數據記錄的列表，每條記錄以 dict 形式儲存。
	"""
	data = []
	with open(file_path, 'rb') as file:  # 使用二進位讀取資料
		buffer = b''
		while True:
			chunk = file.read(1024)  # 一次讀取 1024 位元
			if len(chunk) == 0:
				if buffer:
					process_chunk(buffer, data)
				break  # 文件結束

			buffer += chunk

			# 如果 buffer 存在 TERMINAL_CODE
			while TERMINAL_CODE in buffer:
				record_end = buffer.index(TERMINAL_CODE) + len(TERMINAL_CODE)
				record = buffer[:record_end]
				buffer = buffer[record_end:]

				# 檢查記錄是否以 ESC_CODE 開頭
				if record.startswith(ESC_CODE):
					# 檢查是否跳過資料
					if skip_conditions and should_skip(record, skip_conditions):
						continue  # 跳過該資料

					process_chunk(record, data)  # 處理完整記錄

	return data



def should_skip(record: bytes, skip_conditions: List[Dict[str, Union[int, Tuple[int, int], str]]]) -> bool:
	"""
	判斷是否需要跳過該筆資料。
	
	參數:
	record(bytes): 要檢查的記錄數據。
	skip_conditions(list): 包含多個條件的列表，每個條件是包含位置、指定數值和模式的 dict。
	
	輸出:
	bool: 如果需要跳過，返回 True，否則返回 False。
	"""
	# 紀錄 include 條件的匹配結果
	include_matches = []
	# 紀錄 exclude 條件的匹配結果
	exclude_matches = []

	for condition in skip_conditions:
		position = condition['position']
		value, mask = condition['value']
		mode = condition['mode']
		
		# 確保記錄長度足夠
		if len(record) <= position:
			continue
		
		# 檢查指定位置的值是否符合條件
		record_value = record[position] & mask
		match = (record_value == value)
		
		if mode == 'include':
			include_matches.append(match)
		elif mode == 'exclude':
			exclude_matches.append(match)
	
	# 根據條件集合來判斷是否跳過
	# include 所有條件都必須成立（取交集），include_result 為 True。
	include_result = all(include_matches) if include_matches else True
	# exclude 任一條件成立（取聯集），exclude_result 為 False。
	exclude_result = any(exclude_matches) if exclude_matches else False

	# 如果 not include_result，或 exclude_result，其中一個為 True，記錄會被跳過（返回 True ）。
	return not include_result or exclude_result



def process_chunk(chunk: bytes, data: List[Dict[str, Any]]) -> None:
	"""
	處理單一筆數據記錄，解析其中的各部分並將結果添加到data。

	參數:
	chunk (bytes): 單一筆數據記錄。
	data (list): 用於儲存解析後記錄的列表。

	返回:
	None
	"""

	# 檢查資料長度是否符合最小要求
	if len(chunk) < 19:
		return  # 跳過不完整紀錄(沒有BODY)

	# 解析 ESC-CODE
	esc_code = decode_ascii(chunk[0:1])  # 位置 1，長度 1

	# 解析 HEADER
	header = {
		'message_length': decode_packed_bcd(chunk[1:3]),  # 位置 2-3，長度 2 (PACKED BCD)
		'business_code': decode_packed_bcd(chunk[3:4]),   # 位置 4，長度 1 (PACKED BCD)
		'format_code': decode_packed_bcd(chunk[4:5]),     # 位置 5，長度 1 (PACKED BCD)
		'format_version': decode_packed_bcd(chunk[5:6]),  # 位置 6，長度 1 (PACKED BCD)
		'transmission_number': decode_packed_bcd(chunk[6:10])  # 位置 7-10，長度 4 (PACKED BCD)
	}

	# 解析 BODY

	# 提取即時行情的價格和數量
	offset = 29
	prices = []
	quantities = []
	# 剩餘的長度小於 9 位，退出迴圈。
	while offset + 9 <= len(chunk) - len(TERMINAL_CODE):  # 減去TERMINAL_CODE長度
		price = chunk[offset:offset + 5]  # 長度 5 (PACKED BCD)
		quantity = chunk[offset + 5:offset + 9]  # 長度 4 (PACKED BCD)
		prices.append(price)
		quantities.append(quantity)
		offset += 9

	# 轉換 BIT MAP 紀錄之資料
	reveal_flags = convert_reveal_flags(chunk[22:23])  # 位置 23，長度 1 (BIT MAP)
	limit_flags =  convert_limit_flags(chunk[23:24])  # 位置 24，長度 1 (BIT MAP)
	status_flags = convert_status_flags(chunk[24:25])  # 位置 25，長度 1 (BIT MAP)

	# 轉換證券代碼
	stock_code =  decode_ascii(chunk[10:16])     # 位置 11-16，長度 6 (ASCII)
	total_volume = decode_packed_bcd(chunk[25:29])    # 位置 26-29，長度 4 (PACKED BCD)

	body = {
		'stock_code': stock_code,
		'matching_time': convert_match_time(chunk[16:22]),  # 位置 17-22，長度 6 (PACKED BCD，需轉換時間格式)
		'reveal_flags': reveal_flags,  
		'limit_flags': limit_flags,
		'status_flags': status_flags,   
		'total_volume': format_number_string(total_volume, decimal_digits=0),
		'instant_quotes': convert_instant_quotes(
			prices, 
			quantities, 
			reveal_flags,
			limit_flags, 
			status_flags,
			stock_code
		)
	}

	# 解析檢查碼
	check_code = calculate_checksum(chunk[1:-len(TERMINAL_CODE)])  # 從第二個字節到倒數 TERMINAL_CODE 之前

	# 解析 TERMINAL-CODE
	terminal_code = decode_hexacode(chunk[-len(TERMINAL_CODE):])  # TERMINAL-CODE 位置

	# 合併資料
	data.append({
		'esc_code': esc_code,
		'header': header,
		'body': body,
		'check_code': check_code,
		'terminal_code': terminal_code,
	})