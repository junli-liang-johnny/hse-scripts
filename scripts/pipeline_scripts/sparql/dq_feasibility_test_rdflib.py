#!/usr/bin/env python3
"""
DQ feasibility test using RDFlib (no triplestore required)

need to change this column into Data feasibility for OAHWP result:  
Pass = DQ tests 1.7, 2,3  pass, metadata is not present
Fail = DQ tests 1.7, 2,3 fail AND metadata is present in the critical fields 
Unknown = DQ tests 1.7, 2,3 fail AND no metadata is present in the critical fields ie we are unsure if the indicator would pass or fail, we just don't have the data

Data protection column has three states:
1. No personal data
2. Some personal data
3. High risk personal data
"""
import os
import argparse
import pandas as pd
from rdflib import Graph

def load_rdf_data(rdf_files):
    """Load RDF files into a single graph"""
    g = Graph()
    for rdf_file in rdf_files:
        if not os.path.exists(rdf_file):
            print(f"Warning: RDF file not found: {rdf_file}")
            continue
        print(f"Loading {rdf_file}...")
        g.parse(rdf_file, format='turtle')
    print(f"Loaded {len(g)} triples")
    return g

def feasibility_check(graph, query_file):
    """Execute the feasibility_check.rq query against the RDFlib graph"""
    from rdflib.namespace import Namespace
    
    # Read the SPARQL query
    with open(query_file, 'r', encoding='utf-8') as f:
        query = f.read()
    
    # Define namespaces explicitly for RDFlib
    initNs = {
        'xsd': Namespace('http://www.w3.org/2001/XMLSchema#'),
        'ddc': Namespace('http://purl.org/NET/decimalised#'),
        'dpv': Namespace('https://w3id.org/dpv#'),
        'dcterm': Namespace('http://purl.org/dc/terms/'),
        'dct': Namespace('http://purl.org/dc/terms/'),
        'dcterms': Namespace('http://purl.org/dc/terms/'),
        'dc': Namespace('http://purl.org/dc/elements/1.1/'),
        'dcat': Namespace('http://www.w3.org/ns/dcat#'),
        'skos': Namespace('http://www.w3.org/2004/02/skos/core#'),
        'prov': Namespace('http://www.w3.org/ns/prov#'),
        'adms': Namespace('http://www.w3.org/ns/adms#'),
        'foaf': Namespace('http://xmlns.com/foaf/0.1/'),
        'phi': Namespace('https://hse.ie/ontology/phi#'),
        'phd': Namespace('https://hse.ie/ontology/phd#'),
        'phpt': Namespace('https://hse.ie/terminology/phpt#'),
        'healthdcatap': Namespace('http://healthdata.dublinked.ie/def/healthdcatap#'),
        'owl': Namespace('http://www.w3.org/2002/07/owl#'),
    }
    
    # Execute query with namespace bindings
    results = graph.query(query, initNs=initNs)
    
    # Get variable names
    var_names = [str(var) for var in results.vars]
    print(f"Headers: {var_names}")
    
    # Convert results to list of dicts
    data = []
    for row in results:
        result_dict = {}
        for var in results.vars:
            var_name = str(var)
            value = row[var]
            if value is not None:
                result_dict[var_name] = str(value)
            else:
                result_dict[var_name] = ""
        data.append(result_dict)
    
    if data:
        print(f"First result: {data[0]}")
    else:
        print("No results")
    
    return data

def convert2_dq_table(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the DataFrame to the desired DQ table format"""
    dq_table = df.copy()
    # Apply any necessary transformations to match the DQ table structure
    dq_table['Indicator ID'] = dq_table['indicator'].apply(lambda x: x.split('/')[-1] if isinstance(x, str) else '')
    dq_table['DQ Pass'] = dq_table['pass']
    dq_table['DQ Score'] = dq_table['dq_score']

    # append warning notes from '1_7_warning', '2_1_warning', '2_2_warning', '3_1_warning' if they are not empty
    def combine_warnings(row):
        warnings = []
        if row.get('1_7_warning'):
            warnings.append(row['1_7_warning'])
        if row.get('1_7_note'):
            warnings.append(row['1_7_note'])
        if row.get('2_1_warning'):
            warnings.append(row['2_1_warning'])
        if row.get('2_1_note'):
            warnings.append(row['2_1_note'])
        if row.get('2_2_warning'):
            warnings.append(row['2_2_warning'])
        if row.get('3_1_warning'):
            warnings.append(row['3_1_warning'])
        if row.get('3_1_note'):
            warnings.append(row['3_1_note'])
        if row.get('data_protection_warning'):
            warnings.append(row['data_protection_warning'])
        return '; '.join(warnings)
    dq_table['Warning'] = dq_table.apply(combine_warnings, axis=1)

    def tests_not_passed_row(row):
        failed = []
        # 1.1
        if row.get('1_1_pass') == 'false' or row.get('1_1_pass') == 'unknown':
            failed.append('Q1.1')
        # 1.7
        if row.get('1_7_pass') == 'false' or row.get('1_7_pass') == 'unknown':
            failed.append('Q1.7')
        # 2.1
        if row.get('2_1_pass') == 'false' or row.get('2_1_pass') == 'unknown':
            failed.append('Q2.1')
        # 2.2
        if row.get('2_2_pass') == 'false' or row.get('2_2_pass') == 'unknown':
            failed.append('Q2.2')
        # 3.1
        if row.get('3_1_pass') == 'false' or row.get('3_1_pass') == 'unknown':
            failed.append('Q3.1')
        if row.get('4_1_pass') == 'false' or row.get('4_1_pass') == 'unknown':
            failed.append('Q4.1')
        if row.get('4_2_pass') == 'false' or row.get('4_2_pass') == 'unknown':
            failed.append('Q4.2')
        if row.get('4_3_pass') == 'false' or row.get('4_3_pass') == 'unknown':
            failed.append('Q4.3')

        return failed

    dq_table['Tests Not Passed'] = dq_table.apply(lambda row: ', '.join(tests_not_passed_row(row)), axis=1)
    # not passed Reasons: combine all *_note columns if not empty, prefix with test id
    note_cols = [
        '1_1_note',
        '2_2_note',
    ]
    # skip empty notes
    def failure_reasons_row(row):
        reasons = []
        for col in note_cols:
            if row.get(col) and row[col].strip():
                reasons.append(f"{row[col]}")
        return '; '.join(reasons)
    dq_table['Reasons'] = dq_table.apply(failure_reasons_row, axis=1)

    # Drop intermediate columns
    columns_to_drop = [
      'indicator',
       'indicatorTitle', 
       'dq_score',
       '1_1_pass',
       '1_1_note',
       '1_7_pass', 
       '1_7_note', 
       '1_7_warning',
       '2_1_pass', 
       '2_1_note', 
       '2_1_warning',
       '2_2_pass', 
       '2_2_note', 
       '2_2_warning',
       '3_1_pass', 
       '3_1_note', 
       '3_1_warning',
       'valid_dataset', 
       'pass', 
       '4_1_pass',
       '4_1_warning',
       '4_2_pass',
       '4_2_warning',
       '4_3_pass',
       '4_3_warning',
       'data_protection_pass',
       'data_protection_warning',
      ]
    dq_table = dq_table.drop(columns=columns_to_drop)

    return dq_table

def main():
    parser = argparse.ArgumentParser(description="DQ feasibility test using RDFlib")
    parser.add_argument("--rdf-files", "-r", nargs='+', required=True, help="RDF files to load (TTL format)")
    parser.add_argument("--query-file", "-q", default="sparql/v2/feasibility_check.rq", help="SPARQL query file")
    parser.add_argument("-o", "--output-csv", default="output.csv", help="Output CSV file")
    args = parser.parse_args()

    # Load RDF data
    graph = load_rdf_data(args.rdf_files)
    
    # Execute query
    print(f"Executing query from {args.query_file}...")
    feasibility_check_results = feasibility_check(graph, args.query_file)
    
    # Convert to DataFrame
    feasibility_results_df = pd.DataFrame(feasibility_check_results)
    feasibility_results_df.to_csv(args.output_csv, index=False)
    print(f"Results written to {args.output_csv}")

    print("Converting to DQ table format...")
    dq_table_df = convert2_dq_table(feasibility_results_df)
    dq_table_output_path = args.output_csv.replace(".csv", "_dq_table.csv")
    dq_table_df.to_csv(dq_table_output_path, index=False)
    print(f"DQ table results written to {dq_table_output_path}")

if __name__ == "__main__":
    main()
