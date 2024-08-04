# src/main.py

import json
import argparse
from parser import parse_file

# 定義情境條件
scenario_conditions = {
	'reveal_flags': [
		{"position": 22, "value": (0b10000000, 0b00000000)},
		{"position": 22, "value": (0b10000000, 0b10000000)}
	],
	'limit_flags': [
		{"position": 23, "value": (0b11000000, 0b00000000)},
		{"position": 23, "value": (0b11000000, 0b01000000)},
		{"position": 23, "value": (0b11000000, 0b10000000)}
	],
	'status_flags': [
		{"position": 24, "value": (0b10000000, 0b00000000)},
		{"position": 24, "value": (0b10000000, 0b10000000)}
	]
}

def parse_scenarios(scenarios_str):
	"""
	解析情境條件字串，生成相應的跳過條件列表。

	參數:
	scenarios_str (str): 包含情境條件的字串，使用逗號分隔，每個條件由位置和模式組成（例如："1:include,2:exclude"）。

	返回:
	list: 包含跳過條件的字典列表，每個字典包含位置、數值、模式等資訊。
	"""
	skip_conditions = []

	# 如果情境條件字串為空，返回空 list
	if not scenarios_str:
		return skip_conditions

	# 使用逗號分隔情境條件字串
	scenarios = scenarios_str.split(',')
	# 定義不同位置對應的情境條件類型
	flag_types = ['reveal_flags', 'limit_flags', 'status_flags']

	for i, scenario in enumerate(scenarios):
		# 如果條件為 '0'，則跳過該條件
		if scenario == '0':
			continue

		# 解析情境條件中的位置和模式
		index, mode = scenario.split(':')
		index = int(index) - 1
		flag_type = flag_types[i]

		# 從預定義的情境條件中複製對應的條件
		condition = scenario_conditions[flag_type][index].copy()
		# 設置條件的模式（include 或 exclude）
		condition['mode'] = mode
		skip_conditions.append(condition)

	return skip_conditions



def main():

	# 初始化 ArgumentParser 物件，用於處理命令行參數
	parser = argparse.ArgumentParser(description="Parse binary data file with dynamic skip conditions.")
	
	# 添加輸入檔案參數
	parser.add_argument(
		'input_file',
		type=str,
		help='Name of the input data file (located in data/raw directory)'
	)
	
	# 添加輸出檔案參數
	parser.add_argument(
		'output_file',
		type=str,
		help='Name of the output JSON file (located in data/processed directory)'
	)
	
	# 添加情境條件參數（可選）
	parser.add_argument(
		'--scenarios',
		type=str,
		default='',
		help='Comma-separated list of scenarios and modes (e.g., "1:include,2:exclude,3:include")'
	)
	# 解析命令列參數
	args = parser.parse_args()
	
	# 生成檔案路徑
	data_file = f'data/raw/{args.input_file}'
	output_file = f'data/processed/{args.output_file}'

	# 解析 scenarios 參數
	skip_conditions = parse_scenarios(args.scenarios)

	# 解析原始資料
	data = parse_file(data_file, skip_conditions)

	# 將轉換後資料保存成 JSON
	with open(output_file, 'w', encoding='utf-8') as json_file:
		json.dump(data, json_file, ensure_ascii=False, indent=4)

	print(f'Data has been successfully written to {output_file}')

if __name__ == "__main__":
	main()