import pandas as pd
import argparse

columns = [
	'dcterms:title',
	'dct:identifier',
	'owl:sameAs',
	# 'rdf:type', # i.e. hwbp:Indicator, dcat:Dataset or dcat:DatasetSeries
	'skos:note',
	'dct:provenance [a dct:ProvenanceStatement;rdfs:label ]', # ie put "Created for Older Adult Health and Wellbeng Profile Project 2025" AND if there are other indicators put "Original source <organisation_name>" where org name is eg CSO or TILDA
]

def extract_columns(df):
	return df[columns]

def normalise_prov_col(df: pd.DataFrame) -> pd.DataFrame:
	prov_col = 'dct:provenance [a dct:ProvenanceStatement;rdfs:label ]'
	common_prov = 'Created for Older Adult Health and Wellbeing Profile Project 2025'
	for index, row in df.iterrows():
		prov_val = str(row.get(prov_col, ''))
		if 'CSO' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source CSO'
		elif 'TILDA' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source TILDA'
		elif 'Department of Government and Housing' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source Department of Government and Housing'
		elif 'HIPE' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source HIPE'
		elif 'HPSC' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source HPSC'
		elif 'ICPOP' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source ICPOP'
		elif 'NBIU' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source NBIU'
		elif 'Patient experience time' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source Patient experience time'
		elif 'Pobal' in prov_val:
			df.at[index, prov_col] = f'{common_prov}. Original source Pobal'
		else:
			df.at[index, prov_col] = common_prov  # Default value if no specific source is found

	return df

def add_rdf_type(df: pd.DataFrame, rdf_type='hwbp:Indicator', **kwags) -> pd.DataFrame:
	row = kwags.get('row')
	col = kwags.get('col')
	if row and col:
		df.at[row, col] = rdf_type
	else:
		df['rdf:type'] = rdf_type

	return df

def main():
	parser = argparse.ArgumentParser(description='Process some data.')
	parser.add_argument('--input-file', type=str, help='Path to the input CSV file')
	parser.add_argument('--output-file', type=str, help='Path to the output CSV file')
	args = parser.parse_args()

	df = pd.read_csv(args.input_file)
	extracted = extract_columns(df)
	extracted = normalise_prov_col(extracted)
	extracted = add_rdf_type(extracted)
	extracted.dropna(how='all', inplace=True)  # Remove rows where all elements are NaN
	extracted.to_csv(args.output_file, index=False)

if __name__ == '__main__':
	main()