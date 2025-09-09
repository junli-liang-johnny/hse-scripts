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
#     query = f"""
#     {prefix}

# SELECT 
# ?indicator 
# ?indicatorTitle
# ?pass
# ?with_dataset
# ?1_7_pass
# ?1_7_note
# ?2_1_pass
# ?2_1_note
# ?2_2_pass
# ?2_2_note
# ?3_1_pass
# ?3_1_note
# ?3_2_pass
# ?3_2_note
# WHERE {{
#   ?indicator a phi:Indicator ;
#   a dcat:Dataset .
#   ?indicator dcterms:title ?indicatorTitle .

#   OPTIONAL {{ ?indicator  phi:numeratorSource ?numeratorSource . }}
#   OPTIONAL {{ ?indicator dcterms:accrualPeriodicity ?indicatorAccrualPeriodicity . }}
#   OPTIONAL {{ ?indicator phi:disaggregation ?disaggregation . }}
#   OPTIONAL {{ ?indicator phi:reportStyle ?reportStyle .}}
#   OPTIONAL {{ ?numeratorSource dcat:temporalResolution ?temporalResolution . }}
#   OPTIONAL {{ ?numeratorSource phd:SpatialAggregationCode ?SpatialAggregationCode . }}
#   OPTIONAL {{ ?numeratorSource dcat:spatialResolutionInMeters ?spatialResolutionInMeters . }}
#   OPTIONAL {{ ?numeratorSource dcterms:accrualPeriodicity ?datasetAccrualPeriodicity . }}

#   # with dataset?
#   BIND(BOUND(?numeratorSource) AS ?with_dataset)
#   # 1.7
#   BIND(IF(!BOUND(?disaggregation), false, IF(CONTAINS(LCASE(STR(?disaggregation)), "65 years"), true, false)) AS ?1_7_pass)
#   BIND(IF(!BOUND(?disaggregation), "Disaggregation not present", IF(CONTAINS(LCASE(STR(?disaggregation)), "65 years"), "Q1.7 pass", "Q1.7 fail")) AS ?1_7_note)
#   # 2.1
#   BIND(BOUND(?temporalResolution) AS ?2_1_pass)
#   BIND(IF(BOUND(?temporalResolution), "Q2.1 pass", "Minimal Temporal resolution not present") AS ?2_1_note)
#   # 2.2
#   BIND(IF(!BOUND(?SpatialAggregationCode), false, 
#       IF(?SpatialAggregationCode = phpt:National || ?SpatialAggregationCode = phpt:IHA || ?SpatialAggregationCode = phpt:NUTS1, true, false)) 
#     AS ?2_2_pass)
#   BIND(IF(!BOUND(?SpatialAggregationCode), "Saptial Resolution Code not present", 
#       IF(?SpatialAggregationCode = phpt:National || ?SpatialAggregationCode = phpt:IHA || ?SpatialAggregationCode = phpt:NUTS1, "Q2.2 pass", "Q2.2 fail")) 
#     AS ?2_2_note)
#   # 3.1
#   BIND(IF(!BOUND(?indicatorAccrualPeriodicity), false, 
#       IF(!BOUND(?datasetAccrualPeriodicity), false, 
#         IF(?indicatorAccrualPeriodicity = ?datasetAccrualPeriodicity, true, false)))
#     AS ?3_1_pass)
#   BIND(IF(!BOUND(?indicatorAccrualPeriodicity), "Indicator Report Frequency not present", 
#       IF(!BOUND(?datasetAccrualPeriodicity), "Dataset Update Frequency not present", 
#         IF(?indicatorAccrualPeriodicity = ?datasetAccrualPeriodicity, "Q3.1 pass", "Q3.1 fail"))) 
#     AS ?3_1_note)
#   # 3.2
#   BIND(IF(BOUND(?reportStyle), true, false) AS ?3_2_pass)
#   BIND(IF(BOUND(?reportStyle), "Q3.2 pass", "Report Style not present") AS ?3_2_note)
#   # pass or fail
#   BIND(IF((?1_7_pass && ?2_1_pass && ?2_2_pass && ?3_1_pass && ?3_2_pass), true, false) AS ?pass)
# }}
#     """
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

  data_protection_warning = data_protection_warning_check(sparql, [])
  # print(f"data_protection_warning: {data_protection_warning}")

  feasibility_check_results = feasibility_check(sparql, [])
  # print(f"feasibility_check_results: {feasibility_check_results}")
  merged = pd.merge(
    pd.DataFrame(feasibility_check_results),
    pd.DataFrame(data_protection_warning),
    on="indicator",
    how="left",
    suffixes=("", "_y")
  )
  merged = merged.drop(columns=[col for col in merged.columns if col.endswith("_y")])
  merged.to_csv(output_csv, index=False)
  print(f"Results written to {output_csv}")

if __name__ == "__main__":
  main()