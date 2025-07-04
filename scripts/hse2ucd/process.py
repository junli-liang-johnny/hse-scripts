from scripts.hse2ucd.config import mapping_rules_file, indicators_output_file, datasets_output_file, datasets_additional_headers, datasets_headers_insert_indices, indicaotrs_additional_headers, indicators_insert_indices
from scripts.hse2ucd.load_mapping_rules import load_mapping_rules
from scripts.hse2ucd.load_process_files import load_process_files
from scripts.csv_utils import write_csv, validate_csv, insert_additional_headers
from scripts.validate.csv_validate import clean_csv

def process_hse2ucd(output_file: str, mapping_rules: dict, input_data_header: list[str], data_to_process: list[list[str]]):
		"""
		Process the HSE2UCD dataset.
		"""
		# Placeholder for processing logic
		print("Processing HSE2UCD dataset...")
		print(f"input_data_header: {input_data_header}")
		ucd_fields = list(mapping_rules.keys())
		hse_fields = list(mapping_rules.values())
		hse_field_index_list: list[int] = []
		input_field_index_list: list[int] = []
		target_csv = []
		print(f"UCD fields: {ucd_fields}")
		print(f"HSE fields: {hse_fields}")

		# append header to target_csv
		target_csv.append(ucd_fields)

		for ucd_field in ucd_fields:
			hse_field = mapping_rules[ucd_field]
			# print(f"Processing field: {ucd_field} -> {hse_field}")
			if hse_field is not None:
				# Find the index of the field in the file
				hse_field_index = hse_fields.index(hse_field)
				field_index = input_data_header.index(hse_field)
				# hse_field_index_list.append({'hse_field_index': hse_field_index, 'input_field_index': field_index})
				hse_field_index_list.append(hse_field_index)
				input_field_index_list.append(field_index)
		print(f"HSE field index list: {hse_field_index_list}")
		print(f"Input field index list: {input_field_index_list}")

		# Iterate through the data to process
		for hse_file in data_to_process:
			for row in hse_file:
				new_row = []
				for ucd_field_index in range(len(ucd_fields)):
					if ucd_field_index in hse_field_index_list:
						new_row.append(row[input_field_index_list[hse_field_index_list.index(ucd_field_index)]])
					else:
						new_row.append('')
				target_csv.append(new_row)

		# save the processed files to target_csv
		write_csv(output_file, target_csv)

		# For example, loading data, transforming it, etc.
		print("HSE2UCD processed successfully.")

if __name__ == "__main__":
	indicators_dict_rules, datasets_dict_rules = load_mapping_rules(mapping_rules_file)
	header, process_files = load_process_files()

	# Process the HSE2UCD indicators
	process_hse2ucd(indicators_output_file, indicators_dict_rules, header, process_files)
	# Process the HSE2UCD datasets
	process_hse2ucd(datasets_output_file, datasets_dict_rules, header, process_files)

	# validate the output file
	if validate_csv(indicators_output_file, list(indicators_dict_rules.keys())):
		print(f"Validation of {indicators_output_file} passed.")
	else:
		print(f"Validation of {indicators_output_file} failed.")

	if validate_csv(datasets_output_file, list(datasets_dict_rules.keys())):
		print(f"Validation of {datasets_output_file} passed.")
	else:
		print(f"Validation of {datasets_output_file} failed.")

	# clean the output files
	clean_csv(indicators_output_file, indicators_output_file)
	clean_csv(datasets_output_file, datasets_output_file)

	# insert additional headers
	# insert_additional_headers(indicators_output_file, indicaotrs_additional_headers, indicators_insert_indices)
	# insert_additional_headers(datasets_output_file, datasets_additional_headers, datasets_headers_insert_indices)