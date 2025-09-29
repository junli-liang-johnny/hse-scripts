import csv
import requests
import sys
import re
import os

# Input and output file paths
INPUT_CSV = 'cso_tables2.csv'
OUTPUT_CSV = 'dataset_Population.csv'

# Define the columns for the output CSV
FIELDNAMES = [
    'Dataset Name',
    'URL (identifier)',
    'Publisher Name',
    'Description',
    'Data Creator (Organisation)',
    'Status',
    'Provenance',
    'Main Point of Contact',
    'Type of Data',
    'Frequency of data updates',
    'Data Coverage Start Date',
    'Data Coverage End Date',
    'Minimum Temporal Resolution',
    'Region Covered',
    'Spatial Resolution',
    'Language',
    'Documentation',
    'Access Rights',
    'Relevance to Older Persons Health & Wellbeing',
    'Flag specific issues e.g. data availability/access (or other issues)',
    'Contains Personal Data',
    'Data Controller',
    'Has Legal Basis',
    'File Format',
    'Link to Dataset Sample',
    'Keywords',
    'Theme',
    'Applicable Legislation',
    'Publisher Type',
    'Health data access body',
    'Health Data Category',
    'Health Theme',
    'Conforms to Standard',
    'Has Coding Scheme',
    'Minimum Typical Age',
    'Maximum Typical Age',
    'Population coverage',
    'In Series',
    'Number of records for unique individuals.',
    'Notes'
]

# Constants for fixed fields
PUBLISHER_NAME = 'CSO'
TYPE_OF_DATA = 'Statistical'
FILE_FORMAT = 'JSON-stat 2.0'
REGION = 'Ireland'
SPATIAL_RESOLUTION = 'Ireland'
ACCESS_RIGHT = 'Public'
RELEVENCE = 'from cso older person cso hub'
PERSONAL_DATA = 'dpv:NonPersonalData'
DATA_CONTROLER = 'CSO'
FILE_FORMAT = 'CSV, JSON-Stat 2.0, JSON-stat 1.0, PX, XLSX'
PUBLISHER_TYPE = 'Statistical Agency '
HELTH_DATA_ACCESS_BODY = 'HIQA'




def main():
    # Read input metadata
    try:
        with open(INPUT_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Input file '{INPUT_CSV}' not found.")
        sys.exit(1)

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for row in rows:
            json_meta_url = row.get('Json_Meta', '').strip()
            link = row.get('Link', '').strip()
            frequency = row.get('Frequency', '').strip()
            provenance = ''
            
            if not json_meta_url:
                print(f"Skipping row without Json_Meta: {link}")
                continue

            # Fetch JSON-stat metadata
            try:
                resp = requests.get(json_meta_url)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"Error fetching JSON '{json_meta_url}': {e}")
                continue

            # Populate fields from JSON
            dataset_name = data.get('label', '').strip()
            description = data.get('description', '').strip()
            creator = data.get('extension',{}).get('copyright', {}).get('name', '').strip()
            provenance = data.get('copyright', {}).get('code', '').strip()
            status = data.get('status', '')
            note_list = data.get('note', [])
            if isinstance(note_list, list) and len(note_list) > 1:
                notes = note_list[1].strip()
            elif isinstance(note_list, list) and len(note_list) == 1:
                notes = note_list[0].strip()
            else:
                notes = ''
            # Determine data coverage dates from TLIST dimension
            start_date = ''
            end_date = ''
            for dim_key, dim_val in data.get('dimension', {}).items():
                if dim_key.startswith('TLIST'):
                    index = dim_val.get('category', {}).get('index', [])
                    if index:
                        start_date = index[0]
                        end_date = index[-1]
                    break

            # Determine min/max typical age from Age Group dimension
            min_age = ''
            max_age = ''
            for dim_key, dim_val in data.get('dimension', {}).items():
                if dim_val.get('label', '') == 'Age Group':
                    cat = dim_val.get('category', {})
                    idx = cat.get('index', [])
                    labels = cat.get('label', {})
                    if idx:
                        first = labels.get(idx[0], '')
                        last = labels.get(idx[-1], '')
                        m1 = re.search(r"(\d+)", first)
                        m2 = re.search(r"(\d+)", last)
                        if m1:
                            min_age = m1.group(1)
                        if m2:
                            max_age = m2.group(1)
                    break

            # Construct record
            record = {
                'Dataset Name': dataset_name,
                'URL (identifier)': link,
                'Publisher Name': PUBLISHER_NAME,
                'Description': description,
                'Data Creator (Organisation)': creator,
                'Status': status,
                'Provenance': provenance,
                'Main Point of Contact': '',
                'Type of Data': TYPE_OF_DATA,
                'Frequency of data updates': frequency,
                'Data Coverage Start Date': start_date,
                'Data Coverage End Date': end_date,
                'Minimum Temporal Resolution': '',
                'Region Covered': REGION,
                'Spatial Resolution': SPATIAL_RESOLUTION,
                'Language': '',
                'Documentation': '',
                'Access Rights': ACCESS_RIGHT,
                'Relevance to Older Persons Health & Wellbeing': RELEVENCE,
                'Flag specific issues e.g. data availability/access (or other issues)': '',
                'Contains Personal Data': PERSONAL_DATA,
                'Data Controller': DATA_CONTROLER,
                'Has Legal Basis': '',
                'File Format': FILE_FORMAT,
                'Link to Dataset Sample': '',
                'Keywords': '',
                'Theme': '',
                'Applicable Legislation': '',
                'Publisher Type': PUBLISHER_TYPE,
                'Health data access body': HELTH_DATA_ACCESS_BODY,
                'Health Data Category': '',
                'Health Theme': '',
                'Conforms to Standard': '',
                'Has Coding Scheme': '',
                'Minimum Typical Age': min_age,
                'Maximum Typical Age': max_age,
                'Population coverage': '',
                'In Series': '',
                'Number of records for unique individuals.': '',
                'Notes': notes
            }

            writer.writerow(record)
            print(f"Wrote dataset summary for: {dataset_name}")

    print(f"Dataset summary written to '{OUTPUT_CSV}'.")


if __name__ == '__main__':
    main()
