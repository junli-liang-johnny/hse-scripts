import os
import rdflib
import argparse
from SPARQLWrapper import SPARQLWrapper, CSV
import glob

def handle_input_ttl(input_ttl):
    g = rdflib.Graph()
    g.parse(input_ttl, format="ttl")
    return g

def run_sparql(sparql_endpoint, sparql_query, return_header=True):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(CSV)
    results = sparql.query().convert()
    csv_text = results.decode("utf-8")
    if return_header:
        header = csv_text.splitlines()[0]
        csv_content = "\n".join(csv_text.splitlines()[1:]) + "\n"
        return header, csv_content
    else:
        return csv_text

def load_sparql_files(sparql_file_or_folder):
    sparql_queries = []
    if os.path.isdir(sparql_file_or_folder):
      print('Loading SPARQL queries from folder:')
      for filename in os.listdir(sparql_file_or_folder):
        if filename.endswith(".rq"):
          with open(os.path.join(sparql_file_or_folder, filename), "r") as f:
            sparql_queries.append(f.read())
    else:
      print('Loading SPARQL query from file:')
      with open(sparql_file_or_folder, "r") as f:
        sparql_queries.append(f.read())
    return sparql_queries

def main():
    parser = argparse.ArgumentParser(description="Run SPARQL completeness queries on a given RDF file.")
    parser.add_argument("--endpoint", "-e", help="URL of the SPARQL endpoint")
    parser.add_argument("--input-ttl", "-i", help="Path to the input RDF file in Turtle format")
    parser.add_argument("--sparql-file-or-folder", "-s", nargs='+', help="Path(s) to SPARQL file(s) or folder(s)")
    parser.add_argument("--output-csv", "-o", help="Path to the output CSV file")

    args = parser.parse_args()
    sparql_endpoint = args.endpoint
    input_ttl = args.input_ttl
    sparql_sources = args.sparql_file_or_folder
    output_csv = args.output_csv

    sparql_files = []
    for source in sparql_sources:
        if os.path.isdir(source):
            sparql_files.extend(glob.glob(os.path.join(source, "*.rq")))
        elif os.path.isfile(source):
            sparql_files.append(source)
        else:
            print(f"Warning: {source} is not a valid file or folder")
    print(f"Loaded SPARQL files: {len(sparql_files)}")

    # Now sparql_files contains all .rq files from all folders and any individual files
    for i, sparql_file in enumerate(sparql_files):
        with open(sparql_file, "r") as f:
            sparql_query = f.read()

        print(f"sparql_endpoint: {sparql_endpoint}, input_ttl: {input_ttl}, sparql_file_or_folder: {sparql_file}, output_csv: {output_csv}")

        if not sparql_endpoint and not input_ttl:
            print("Error: Missing required arguments.")
            return

        if input_ttl:
            g = handle_input_ttl(input_ttl)
            results = g.query(sparql_query)

            for row in results:
                print(row)

        if sparql_endpoint:
             header, csv_content = run_sparql(sparql_endpoint, sparql_query, return_header=True)

             with open(output_csv, "a") as f:
                if i == 0:
                  f.write(header + "\n")
                f.write(csv_content)
             print(f"Appending results to {output_csv}")

if __name__ == "__main__":
  main()