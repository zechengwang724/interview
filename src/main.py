# src/main.py

import json
from parser import parse_file

# 檔案路徑
data_file = 'data/raw/f6_01000001_01001000_TP03.new'
output_file = 'data/processed/parsed_data.json'

def main():
	# 解析原始資料
	data = parse_file(data_file)

	# 將轉換後資料保存成JSON
	with open(output_file, 'w', encoding='utf-8') as json_file:
	    json.dump(data, json_file, ensure_ascii=False, indent=4)

	print(f'Data has been successfully written to {output_file}')

if __name__ == "__main__":
	main()