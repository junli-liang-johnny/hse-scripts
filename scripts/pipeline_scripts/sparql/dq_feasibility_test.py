import argparse
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

"""
need to change this column into Data feasibility for OAHWP result:  
Pass = DQ tests 1.7, 2,3  pass, metadata is not present
Fail = DQ tests 1.7, 2,3 fail AND metadata is present in the critical fields 
Unknown = DQ tests 1.7, 2,3 fail AND no metadata is present in the critical fields ie we are unsure if the indicator would pass or fail, we just don't have the data

Data protection column has three states:
1. No personal data
2. Some personal data
3. High risk personal data
"""

def feasibility_check(sparql, test_indicators: list[str]) -> list[str]:
  with open("./sparql/v2/feasibility_check.rq", "r", encoding="utf-8") as f:
    query = f.read()
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [
      {
        "indicator": result["indicator"]["value"],
        "indicatorTitle": result["indicatorTitle"]["value"],
        "pass": result["pass"]["value"],
        "dq_score": result["dq_score"]["value"],
        "valid_dataset": result["valid_dataset"]["value"],
        "1_7_pass": result["1_7_pass"]["value"],
        "1_7_note": result["1_7_note"]["value"],
        "2_1_pass": result["2_1_pass"]["value"],
        "2_1_note": result["2_1_note"]["value"],
        "2_2_pass": result["2_2_pass"]["value"],
        "2_2_note": result["2_2_note"]["value"],
        "3_1_pass": result["3_1_pass"]["value"],
        "3_1_note": result["3_1_note"]["value"],
        "4_1_warn": result.get("4_1_warn", {"value": "false"})["value"],
        "4_1_note": result.get("4_1_note", {"value": ""})["value"],
        "4_2_warn": result.get("4_2_warn", {"value": "false"})["value"],
        "4_2_note": result.get("4_2_note", {"value": ""})["value"],
        "4_3_warn": result.get("4_3_warn", {"value": "false"})["value"],
        "4_3_note": result.get("4_3_note", {"value": ""})["value"],
        "data_protection_warning_check": result.get("data_protection_warning_check", {"value": "false"})["value"],
        "data_protection_warning_note": result.get("data_protection_warning_note", {"value": "No personal data"})["value"],
      }
      for result in results["results"]["bindings"]
    ]

def convert2_dq_table(df: pd.DataFrame) -> pd.DataFrame:
    # Convert the DataFrame to the desired DQ table format
    dq_table = df.copy()
    # Apply any necessary transformations to match the DQ table structure
    dq_table['Indicator ID'] = dq_table['indicator'].apply(lambda x: x.split('/')[-1])
    dq_table['DQ Pass'] = dq_table['pass']
    dq_table['DQ Score'] = dq_table['dq_score']

    # data protection column mapping
    dq_table['Data Protection Warning'] = dq_table['data_protection_warning_check']

    def tests_not_passed_row(row):
        failed = []
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
        return failed

    dq_table['Tests Not Passed'] = dq_table.apply(lambda row: ', '.join(tests_not_passed_row(row)), axis=1)
    # Failure Reasons: combine all *_note columns if not empty, prefix with test id
    note_cols = [
        ('1_7_note', 'Q1.7'),
        ('2_1_note', 'Q2.1'),
        ('2_2_note', 'Q2.2'),
        ('3_1_note', 'Q3.1'),
        ('4_1_note', 'Q4.1'),
        ('4_2_note', 'Q4.2'),
        ('4_3_note', 'Q4.3'),
    ]
    def failure_reasons_row(row):
        reasons = [f"{row[col]}" for col, test_id in note_cols if col in row and pd.notna(row[col]) and str(row[col]).strip()]
        return '; '.join(reasons)
    dq_table['Failure Reasons'] = dq_table.apply(failure_reasons_row, axis=1)

    # Drop intermediate columns
    columns_to_drop = [
      'indicator',
       'indicatorTitle', 
       'dq_score',
       '1_7_pass', 
       '1_7_note', 
       '2_1_pass', 
       '2_1_note', 
       '2_2_pass', 
       '2_2_note', 
       '3_1_pass', 
       '3_1_note', 
       'valid_dataset', 
       'pass', 
       '4_1_warn',
       '4_1_note',
       '4_2_warn',
       '4_2_note',
       '4_3_warn',
       '4_3_note',
       'data_protection_warning_check',
       'data_protection_warning_note',
      ]
    dq_table = dq_table.drop(columns=columns_to_drop)

    return dq_table

def main():
  parser = argparse.ArgumentParser(description="DQ feasibility test")
  parser.add_argument("--sparql-endpoint", "-e", default="http://localhost:3030/v5", help="SPARQL endpoint URL")
  parser.add_argument("-o", "--output-csv", default="output.csv", help="Output file")
  args = parser.parse_args()

  sparql_endpoint = args.sparql_endpoint
  # input_ttl = args.input_ttl
  output_csv = args.output_csv

  sparql = SPARQLWrapper(sparql_endpoint)
  sparql.setReturnFormat(JSON)

  feasibility_check_results = feasibility_check(sparql, [])
  feasibility_results_df = pd.DataFrame(feasibility_check_results)
  feasibility_results_df.to_csv(output_csv, index=False)
  print(f"Results written to {output_csv}")

  print("Converting to DQ table format...")
  dq_table_df = convert2_dq_table(feasibility_results_df)
  dq_table_output_path = output_csv.replace(".csv", "_dq_table.csv")
  dq_table_df.to_csv(dq_table_output_path, index=False)
  print(f"DQ table results written to {dq_table_output_path}")

if __name__ == "__main__":
  main()