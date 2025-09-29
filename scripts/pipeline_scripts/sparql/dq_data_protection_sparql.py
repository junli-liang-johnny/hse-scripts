from .hse_sparql_utils import convert_indicator_list_2_str, prefix
from SPARQLWrapper import JSON

def data_protection_warning_check(sparql, test_indicators: list[str]) -> list[str]:
    query = f"""
    {prefix}

    SELECT DISTINCT
    ?indicator
    ?indicatorTitle
    ?hasPersonalData
    ?accessRight
    ?hasDataController
    ?warning
    WHERE {{
      ?indicator a phi:Indicator ;
      dcterms:title ?indicatorTitle .

      OPTIONAL {{ ?indicator phi:numeratorSource ?numeratorSource . }}
      OPTIONAL {{ ?numeratorSource dpv:hasPersonalData ?hasPersonalData . }}
      OPTIONAL {{ ?numeratorSource dcterms:accessRights ?accessRight . }}
      OPTIONAL {{ ?numeratorSource dpv:hasDataController ?hasDataController . }}

  BIND(
    IF(!BOUND(?numeratorSource), "Indicator w/o linked Dataset", 
      IF(!BOUND(?hasPersonalData), "Indicator w/ Dataset potentially contains personal/sensitive data", 
        IF(?hasPersonalData != dpv:NonPersonalData, "Indicator w/ Dataset contains personal data, sensitive personal data or pseudonymised personal data", 
          IF(?hasDataController != "HSE", "Indicator w/ Dataset contains personal/sensitive data that is not controlled by HSE", "No data protection warnings found")
        ))) AS ?warning)

      {convert_indicator_list_2_str(test_indicators)}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [
      {
        "indicator": result.get("indicator", {}).get("value"),
        "indicatorTitle": result.get("indicatorTitle", {}).get("value"),
        "hasPersonalData": result.get("hasPersonalData", {}).get("value"),
        "accessRight": result.get("accessRight", {}).get("value"),
        "hasDataController": result.get("hasDataController", {}).get("value"),
        "warning": result.get("warning", {}).get("value"),
      }
      for result in results["results"]["bindings"]
    ]
    # return [result["indicator"]["value"] for result in results["results"]["bindings"]]

def data_protection_warning_check_4_1(sparql, test_indicators: list[str]) -> list[str]:
    query = f"""
    {prefix}

    SELECT 
    ?indicator 
    ?warning
    WHERE {{
      ?indicator a phi:Indicator ;
        a dcat:Dataset .
      ?indicator  phi:numeratorSource ?numeratorSource .

      ?numeratorSource a dcat:Dataset .

      OPTIONAL {{ ?numeratorSource dpv:hasPersonalData ?hasPersonalData . }}

      BIND(BOUND(?hasPersonalData) as ?hasPersonalDataPresent)
      BIND("Contains personal data, sensitive personal data or pseudonymous data" AS ?warning)

      # FILTER(?hasPersonalData != dpv:NonPersonalData)

      {convert_indicator_list_2_str(test_indicators)}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["indicator"]["value"] for result in results["results"]["bindings"]]

def data_protection_warning_check_4_2(sparql, test_indicators: list[str]) -> list[str]:
    query = f"""
    {prefix}

    SELECT 
    ?indicator 
    ?warning
    WHERE {{
      ?indicator a phi:Indicator ;
        a dcat:Dataset .
      ?indicator  phi:numeratorSource ?numeratorSource .

      ?numeratorSource a dcat:Dataset .

      OPTIONAL {{ ?numeratorSource dpv:hasPersonalData ?hasPersonalData . }}

      BIND(BOUND(?hasPersonalData) as ?hasPersonalDataPresent)
      BIND("Potential data protection issue" AS ?warning)

      FILTER(?hasPersonalDataPresent = false)

      {convert_indicator_list_2_str(test_indicators)}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["indicator"]["value"] for result in results["results"]["bindings"]]

def data_protection_warning_check_4_3(sparql, test_indicators: list[str]) -> list[str]:
    query = f"""
    {prefix}

    SELECT 
    ?indicator 
    ?warning
    WHERE {{
      ?indicator a phi:Indicator ;
        a dcat:Dataset .
      ?indicator  phi:numeratorSource ?numeratorSource .

      ?numeratorSource a dcat:Dataset .

      BIND(BOUND(?hasPersonalData) as ?hasPersonalDataPresent)
      BIND("Dataset with personal data or potential personal data that is not controlled by HSE" AS ?warning)

      OPTIONAL {{ ?numeratorSource dpv:hasPersonalData ?hasPersonalData . }}
      OPTIONAL {{ ?numeratorSource dcterms:accessRights ?accessRight . }}
      OPTIONAL {{ ?numeratorSource dpv:hasDataController ?hasDataController . }}

      FILTER (
        (
          ?hasPersonalData != dpv:NonPersonalData &&
          ?hasDataController = "HSE"
        ) &&
        ?accessRights != "Public"
      )

      {convert_indicator_list_2_str(test_indicators)}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["indicator"]["value"] for result in results["results"]["bindings"]]
