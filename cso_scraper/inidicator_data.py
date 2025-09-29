import csv
import requests
import sys

# Input and output file paths
# INPUT_CSV = 'metadata.csv'
INPUT_CSV = 'cso_tables2.csv'
OUTPUT_CSV = 'indicators_tables_given_Population.csv'

# Define the columns for the output CSV
FIELDNAMES = [
    'Indicator Title',
    'Indicator ID',
    'Rationale',
    'Definition',
    'Indicator Type',
    'Status',
    'Disaggregations',
    'Numerator Data Element',
    'Numerator Source Dataset',
    'Denominator Data Element',
    'Denominator Source Dataset',
    'Methodology',
    'Report Frequency',
    'Report Style',
    'Domain',
    'Subdomain',
    'High-Low Guidance',
    'Measurement Limitations',
    'Validity Guidance',
    'Public Health Importance',
    'Provenance',
    'Notes'
]


def main():
    # Read metadata.csv
    try:
        with open(INPUT_CSV, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Input file {INPUT_CSV} not found.")
        sys.exit(1)

    # Open output CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
        writer.writeheader()

        for row in rows:
            json_meta_url = row.get('Json_Meta', '').strip()
            report_freq = row.get('Frequency', '').strip()
            report_source = row.get('Source', '').strip()
            provenance_code = ''
            notes = ''

            # Fetch JSON-stat metadata
            if not json_meta_url:
                print(f"No Json_Meta URL for row with Link {row.get('Link')}, skipping.")
                continue

            try:
                resp = requests.get(json_meta_url)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"Error fetching JSON from {json_meta_url}: {e}")
                continue

            # Extract dataset-level label (main label)
            main_label = data.get('label', '').strip()
            # Extract provenance code if present
            extensions = data.get('extension', '')
            provenance_code = ''

            # Handle notes
            notes = ''
            raw_notes = data.get('note', '')
            if isinstance(raw_notes, list):
                # Combine all notes into one string
                notes = ' '.join(note.strip() for note in raw_notes if note.strip())
            elif isinstance(raw_notes, str):
                notes = raw_notes.strip()

            if isinstance(extensions, dict):
                provenance_code = extensions.get('copyright', {}).get('code', '')

            # Extract STATISTIC dimension info
            stat_dim = data.get('dimension', {}).get('STATISTIC', {})
            categories = stat_dim.get('category', {})
            codes = categories.get('index', [])
            labels = categories.get('label', {})
            link = row.get('Link', '').strip()

            # Extract other dimension labels for Disaggregations
            disaggregations = []
            for dim_key, dim_val in data.get('dimension', {}).items():
                if dim_key == 'STATISTIC':
                    continue
                dim_label = dim_val.get('label', '').strip()
                if not dim_label:
                    continue

                # If 'Age' in label, get all category labels
                if 'age' in dim_label.lower():
                    age_values = dim_val.get('category', {}).get('label', {}).values()
                    age_str = f'{dim_label} = "' + '","'.join(age_values) + '"'
                    disaggregations.append(age_str)
                else:
                    disaggregations.append(dim_label)

            disagg_str = ','.join(disaggregations)

            # Create a row for each indicator code
            for code in codes:
                # Determine indicator title based on number of codes
                if len(codes) == 1:
                    indicator_title = main_label
                else:
                    title = labels.get(code, '').strip()
                    indicator_title = f"{main_label} - {title}" if main_label else title

                record = {
                    'Indicator Title': indicator_title,
                    'Indicator ID': code,
                    'Rationale': '',
                    'Definition': '',
                    'Indicator Type': '',
                    'Status': '',
                    'Disaggregations': disagg_str,
                    'Numerator Data Element': main_label,
                    'Numerator Source Dataset':link,
                    'Denominator Data Element': '',
                    'Methodology': '',
                    'Report Frequency': report_freq,
                    'Report Style': '',
                    'Domain': '',
                    'Subdomain': '',
                    'High-Low Guidance': '',
                    'Measurement Limitations': '',
                    'Validity Guidance': '',
                    'Public Health Importance': '',
                    'Provenance': provenance_code,
                    'Notes': notes
                }
                writer.writerow(record)
                print(f"Processed indicator {code}: {indicator_title}")

    print(f"All records written to {OUTPUT_CSV}.")


if __name__ == '__main__':
    main()
