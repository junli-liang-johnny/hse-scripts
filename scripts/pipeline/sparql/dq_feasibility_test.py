import argparse
from SPARQLWrapper import SPARQLWrapper, JSON
from .hse_sparql_utils import convert_indicator_list_2_str, prefix
from .dq_data_protection_sparql import data_protection_warning_check
import csv
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


def select_indicator_list(sparql) -> list[str]:
    query = f"""
    {prefix}

    SELECT 
    ?indicator 
    WHERE {{
      ?indicator a phi:Indicator ;
        a dcat:Dataset .
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["indicator"]["value"] for result in results["results"]["bindings"]]

def select_indicator_1_7(sparql, test_indicators: list[str]) -> list[str]:
    query = f"""
    {prefix}

    SELECT 
    ?indicator 
    WHERE {{
      ?indicator a phi:Indicator ;
        a dcat:Dataset .
      ?indicator  phi:numeratorSource ?numeratorSource .

      OPTIONAL {{ ?indicator phi:disaggregation ?disaggregation . }}

      FILTER(CONTAINS(LCASE(STR(?disaggregation)), "65 years"))

      {convert_indicator_list_2_str(test_indicators)}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["indicator"]["value"] for result in results["results"]["bindings"]]

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
        "with_dataset": result["with_dataset"]["value"],
        "1_7_pass": result["1_7_pass"]["value"],
        "1_7_note": result["1_7_note"]["value"],
        "2_1_pass": result["2_1_pass"]["value"],
        "2_1_note": result["2_1_note"]["value"],
        "2_2_pass": result["2_2_pass"]["value"],
        "2_2_note": result["2_2_note"]["value"],
        "3_1_pass": result["3_1_pass"]["value"],
        "3_1_note": result["3_1_note"]["value"],
        "data_protection_warning": result.get("data_protection_warning", {"value": "No personal data"})["value"],
      }
      for result in results["results"]["bindings"]
    ]

def select_indicator_2_1(sparql, test_indicators: list[str]) -> list[str]:
    query = f"""
    {prefix}

    SELECT 
    ?indicator 
    WHERE {{
      ?indicator a phi:Indicator ;
        a dcat:Dataset .
      ?indicator  phi:numeratorSource ?numeratorSource .

      ?numeratorSource a dcat:Dataset ;
        dcterms:title ?numeratorSourceTitle ;
        dcat:temporalResolution ?temporalResolution .

      {convert_indicator_list_2_str(test_indicators)}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["indicator"]["value"] for result in results["results"]["bindings"]]

def select_indicator_2_2(sparql, test_indicators: list[str]) -> list[str]:
    query = f"""
    {prefix}

    SELECT 
    ?indicator 
    WHERE {{
      ?indicator a phi:Indicator ;
        a dcat:Dataset .
      ?indicator  phi:numeratorSource ?numeratorSource .

      ?numeratorSource a dcat:Dataset .
      OPTIONAL {{ ?numeratorSource phd:SpatialAggregationCode ?SpatialAggregationCode . }}
      OPTIONAL {{ ?numeratorSource dcat:spatialResolutionInMeters ?spatialResolutionInMeters . }}

      FILTER(
        ?SpatialAggregationCode = phpt:National || 
        ?SpatialAggregationCode = phpt:IHA || 
        ?SpatialAggregationCode = phpt:NUTS1
      )

      {convert_indicator_list_2_str(test_indicators)}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["indicator"]["value"] for result in results["results"]["bindings"]]

def convert2_dq_table(df: pd.DataFrame) -> pd.DataFrame:
    # Convert the DataFrame to the desired DQ table format
    dq_table = df.copy()
    # Apply any necessary transformations to match the DQ table structure
    dq_table['DQ Pass'] = (
      (dq_table['1_7_pass'] == "true") &
      (dq_table['2_1_pass'] == "true") &
      (dq_table['2_2_pass'] == "true") &
      (dq_table['3_1_pass'] == "true")
    )

    # data protection column mapping
    dq_table['Data Protection Warning'] = dq_table['data_protection_warning']

    def failed_tests_row(row):
        failed = []
        # 1.7
        if row.get('1_7_pass') == 'false':
            failed.append('Q1.7')
        elif row.get('1_7_pass') == 'unknown':
            failed.append('Q1.7 unknown')
        # 2.1
        if row.get('2_1_pass') == 'false':
            failed.append('Q2.1')
        elif row.get('2_1_pass') == 'unknown':
            failed.append('Q2.1 unknown')
        # 2.2
        if row.get('2_2_pass') == 'false':
            failed.append('Q2.2')
        elif row.get('2_2_pass') == 'unknown':
            failed.append('Q2.2 unknown')
        # 3.1
        if row.get('3_1_pass') == 'false':
            failed.append('Q3.1')
        elif row.get('3_1_pass') == 'unknown':
            failed.append('Q3.1 unknown')
        return failed

    dq_table['Failed Tests'] = dq_table.apply(lambda row: ', '.join(failed_tests_row(row)), axis=1)
    # Failure Reasons: combine all *_note columns if not empty, prefix with test id
    note_cols = [
        ('1_7_note', 'Q1.7'),
        ('2_1_note', 'Q2.1'),
        ('2_2_note', 'Q2.2'),
        ('3_1_note', 'Q3.1'),
    ]
    def failure_reasons_row(row):
        reasons = [f"{test_id}: {row[col]}" for col, test_id in note_cols if col in row and pd.notna(row[col]) and str(row[col]).strip()]
        return '; '.join(reasons)
    dq_table['Failure Reasons'] = dq_table.apply(failure_reasons_row, axis=1)

    # Drop intermediate columns
    columns_to_drop = ['indicatorTitle', '1_7_pass', '1_7_note', '2_1_pass', '2_1_note', '2_2_pass', '2_2_note', '3_1_pass', '3_1_note', 'with_dataset', 'pass', 'data_protection_warning']
    dq_table = dq_table.drop(columns=columns_to_drop)

    return dq_table

def main():
  parser = argparse.ArgumentParser(description="DQ feasibility test")
  parser.add_argument("--sparql-endpoint", "-e", default="http://localhost:3030/indicators", help="SPARQL endpoint URL")
  parser.add_argument("-o", "--output-csv", default="output.csv", help="Output file")
  args = parser.parse_args()

  sparql_endpoint = args.sparql_endpoint
  # input_ttl = args.input_ttl
  output_csv = args.output_csv

  sparql = SPARQLWrapper(sparql_endpoint)
  sparql.setReturnFormat(JSON)

  # results = sparql.query().convert()
  # indicator_list = select_indicator_list(sparql)
  # print(f"indicator_list: {indicator_list}")

  # indicator_1_7 = select_indicator_1_7(sparql, indicator_list)
  # print(f"indicator_1_7: {indicator_1_7}")

  # indicator_2_1 = select_indicator_2_1(sparql, indicator_1_7)
  # print(f"indicator_2_1: {indicator_2_1}")

  # indicator_2_2 = select_indicator_2_2(sparql, indicator_2_1)
  # print(f"indicator_2_2: {indicator_2_2}")

  # data_protection_warning = data_protection_warning_check(sparql, [])
  # # print(f"data_protection_warning: {data_protection_warning}")

  # feasibility_check_results = feasibility_check(sparql, [])
  # # print(f"feasibility_check_results: {feasibility_check_results}")
  # merged = pd.merge(
  #   pd.DataFrame(feasibility_check_results),
  #   pd.DataFrame(data_protection_warning),
  #   on="indicator",
  #   how="left",
  #   suffixes=("", "_y")
  # )
  # merged = merged.drop(columns=[col for col in merged.columns if col.endswith("_y")])
  # merged.to_csv(output_csv, index=False)
  # print(f"Results written to {output_csv}")

  feasibility_check_results = feasibility_check(sparql, [])
  feasibility_results_df = pd.DataFrame(feasibility_check_results)
  print(feasibility_results_df.head())
  feasibility_results_df.to_csv(output_csv, index=False)
  print(f"Results written to {output_csv}")

  print("Converting to DQ table format...")
  dq_table_df = convert2_dq_table(feasibility_results_df)
  print(dq_table_df.head())
  dq_table_output_path = output_csv.replace(".csv", "_dq_table.csv")
  dq_table_df.to_csv(dq_table_output_path, index=False)
  print(f"DQ table results written to {dq_table_output_path}")

if __name__ == "__main__":
  main()