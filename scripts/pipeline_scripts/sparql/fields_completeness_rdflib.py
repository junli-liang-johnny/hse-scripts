#!/usr/bin/env python3
"""
Field completeness analysis using RDFlib (no triplestore required)
"""
import os
import sys
import argparse
import pandas as pd
from pathlib import Path
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

def fields_completeness(graph, query_file):
    """Execute the MRO_completeness.rq query against the RDFlib graph"""
    from rdflib.namespace import Namespace
    
    # Read the SPARQL query
    with open(query_file, 'r') as f:
        query = f.read()
    
    # RDFlib has issues with multiple prefixes for the same namespace
    # Replace dct: with dcterms: since they resolve to the same namespace
    query = query.replace('dct:identifier', 'dcterms:identifier')
    query = query.replace('dct:provenance', 'dcterms:provenance')
    
    # Define namespaces explicitly for RDFlib
    initNs = {
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
        'healthdcatap': Namespace('http://healthdata.dublinked.ie/def/healthdcatap#'),
        'owl': Namespace('http://www.w3.org/2002/07/owl#'),
    }
    
    # Execute query with namespace bindings
    results = graph.query(query, initNs=initNs)
    
    # Convert results to list of dicts
    data = []
    for row in results:
        result_dict = {}
        for var in results.vars:
            value = row[var]
            if value is not None:
                result_dict[str(var)] = str(value)
            else:
                result_dict[str(var)] = None
        data.append(result_dict)
    
    return data

def main():
    parser = argparse.ArgumentParser(description="Fields completeness analysis using RDFlib")
    parser.add_argument("--rdf-files", "-r", nargs='+', required=True, help="RDF files to load (TTL format)")
    parser.add_argument("--query-file", "-q", default="sparql/v2/MRO_completeness.rq", help="SPARQL query file")
    parser.add_argument("-o", "--output-csv", default="output.csv", help="Output CSV file")
    args = parser.parse_args()

    # Load RDF data
    graph = load_rdf_data(args.rdf_files)
    
    # Execute query
    print(f"Executing query from {args.query_file}...")
    results = fields_completeness(graph, args.query_file)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Calculate percentages
    percentage_columns = [
        'requiredFieldCompletenessPercent',
        'mandatoryCompletenessPercent',
        'recommendedCompletenessPercent',
        'optionalCompletenessPercent',
        'overallCompletenessPercent'
    ]
    
    # Convert to numeric and format as percentages
    for col in percentage_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Create formatted output (percentages)
    df_formatted = df.copy()
    for col in percentage_columns:
        if col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "")
    
    # Save formatted output
    df_formatted.to_csv(args.output_csv, index=False)
    print(f"Formatted results written to {args.output_csv}")
    
    # Create raw output
    raw_output = args.output_csv.replace('.csv', '_raw.csv')
    df.to_csv(raw_output, index=False)
    print(f"Raw results written to {raw_output}")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    for col in percentage_columns:
        if col in df.columns:
            mean_val = df[col].mean() * 100
            print(f"{col}: {mean_val:.2f}%")

if __name__ == "__main__":
    main()
