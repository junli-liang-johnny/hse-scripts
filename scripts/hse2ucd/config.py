"""
this script defines files to be processed in the pipeline
"""

files2process = [
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Health status.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Child health.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Condition-specific.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Disability.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Health behaviours.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Integrated care.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Mental health.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Older adults.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Social determinants.csv',
	'data/CORE INDICATORS FOR PROFILES 13032025.xlsx - Underserved populations.csv'
]

mapping_rules_file = 'data/HSE2UCD - hse2ucd.csv'

indicators_output_file = 'mapping/indicators_hse2ucd.csv'
datasets_output_file = 'mapping/datasets_hse2ucd.csv'

indicaotrs_additional_headers = [
	[
    'Indicator Title', 'Indicator ID', 'Rationale', 'Definition', 'Indicator Type', 'Status',
    'Disaggregations', 'Numerator Data Element', 'Numerator Source Dataset', 'Denominator Data Element',
    'Denominator Source Dataset', 'Methodology', 'Report Frequency', 'Report Style', 'Domain', 'Subdomain',
    'High-Low Guidance', 'Measurement Limitations', 'Validity Guidance', 'Public Health Importance',
    'Provenance', 'Notes'
	],
	['M', 'M', 'R', 'R', 'M', 'R', 'O', 'R', 'M', 'O', 'O', 'R', 'M', 'R', 'R', 'R', 'O', 'O', 'O', 'R', 'O', 'R']
]

indicators_insert_indices = [0, 2]

datasets_additional_headers = [
	[
    'Dataset Name', 'URL (identifier)', 'Publisher Name', 'Description', 'Data Creator (Organisation)', 'Status',
    'Provenance', 'Main Point of Contact', 'Type of Data', 'Frequency of data updates', 'Data Coverage Start Date',
    'Data Coverage End Date', 'Minimum Temporal Resolution', 'Region Covered', 'Spatial Resolution', 'Language',
    'Documentation', 'Access Rights', 'Relevance to Older Persons Health & Wellbeing',
    'Flag specific issues e.g. data availability/access (or other issues)', 'Contains Personal Data', 'Data Controller',
    'Has Legal Basis', 'File Format', 'Link to Dataset Sample', 'Keywords', 'Theme', 'Applicable Legislation',
    'Publisher Type', 'Health data access body', 'Health Data Category', 'Health Theme', 'Conforms to Standard',
    'Has Coding Scheme', 'Minimum Typical Age', 'Maximum Typical Age', 'Population coverage', 'In Series',
    'Number of records for unique individuals', 'Notes'
	],
	['M', 'M', 'M', 'M', 'O', 'O', 'M', 'M', 'M', 'R', 'R', 'R', 'R', 'M', 'O', 'R', 'O', 'M', 'O', 'O', 'R', 'O', 'R', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'R', 'R', 'R', 'R', 'O', 'O', 'O', 'O'],
	['M', 'M', 'M', 'M', 'O', 'R', 'O', 'M', 'M', 'M', 'R', 'R', 'M', 'M', 'R', 'O', 'O', 'M', 'O', 'O', 'R', 'R', 'O', 'M', 'R', 'O', 'M', 'O', 'O', 'O', 'M', 'M', 'O', 'R', 'M', 'M', 'O', 'O', 'O', 'O']
]

datasets_headers_insert_indices = [0, 2, 3]