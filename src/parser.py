# src/parser.py
# from utils.header.header_parser import parse_header
# from utils.body.body_parser import parse_body

from constants import TERMINAL_CODE
from typing import List, Dict, Any

def parse_file(file_path: str) -> List[Dict[str, Any]]:
    """
    解析二進位數據文件，提取並處理每筆記錄。

    參數:
    file_path(str): 解析的數據文件的路徑。

    輸出:
    list: 包含解析後的數據記錄的列表，每條記錄以dict形式儲存。
    """
    data = []
    with open(file_path, 'rb') as file:  # 使用二進位讀取資料
        buffer = b''
        while True:
            chunk = file.read(1024)  # 一次讀取1024位元
            if len(chunk) == 0:
                if buffer:
                    process_chunk(buffer, data)
                break  # 文件結束
            
            buffer += chunk
            
            # 如果 buffer 存在 TERMINAL_CODE，處理所有完整紀錄
            while TERMINAL_CODE in buffer:
                record_end = buffer.index(TERMINAL_CODE) + len(TERMINAL_CODE)
                record = buffer[:record_end]
                buffer = buffer[record_end:]
                process_chunk(record, data) # 處理完整紀錄

    return data

def process_chunk(chunk: bytes, data: List[Dict[str, Any]]) -> None:
    """
    處理單一筆數據記錄，解析其中的各部分並將結果添加到data。

    參數:
    chunk (bytes): 一筆數據記錄，以字節串形式存儲。
    data (list): 用於存儲解析後記錄的列表。

    返回:
    None
    """

    # 檢查資料長度是否符合最小要求
    if len(chunk) < 19:
        return  # 跳過不完整紀錄

    # 解析 ESC-CODE
    esc_code = chunk[0:1]  # 位置 1，長度 1

    # 解析 HEADER
    header = {
        'message_length': chunk[1:3],  # 位置 2-3，長度 2 (PACKED BCD)
        'business_code': chunk[3:4],   # 位置 4，長度 1 (PACKED BCD)
        'format_code': chunk[4:5],     # 位置 5，長度 1 (PACKED BCD)
        'format_version': chunk[5:6],  # 位置 6，長度 1 (PACKED BCD)
        'transmission_number': chunk[6:10]  # 位置 7-10，長度 4 (PACKED BCD)
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

    body = {
        'stock_code': chunk[10:16],     # 位置 11-16，長度 6 (ASCII)
        'matching_time': chunk[16:22],  # 位置 17-22，長度 6 (PACKED BCD)
        'reveal_item_flag': chunk[22:23],  # 位置 23，長度 1 (BIT MAP)
        'limit_up_down_flag': chunk[23:24],  # 位置 24，長度 1 (BIT MAP)
        'status_flag': chunk[24:25],    # 位置 25，長度 1 (BIT MAP)
        'total_volume': chunk[25:29],    # 位置 26-29，長度 4 (PACKED BCD)
        'instant_quotes': {
            'prices': prices,          # 價格欄位
            'quantities': quantities   # 數量欄位
        }
    }

    # 解析檢查碼
    check_code = chunk[-(len(TERMINAL_CODE) + 1):-len(TERMINAL_CODE)] # TERMINAL-CODE 往前一個位置

    # 解析 TERMINAL-CODE
    terminal_code = chunk[-len(TERMINAL_CODE):]  # TERMINAL-CODE 位置

    # 合併資料
    data.append({
        'esc_code': esc_code,
        'header': header,
        'body': body,
        'check_code': check_code,
        'terminal_code': terminal_code,
    })