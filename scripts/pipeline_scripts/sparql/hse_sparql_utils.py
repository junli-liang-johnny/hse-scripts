prefix = """
PREFIX ddc: <http://purl.org/NET/decimalised#>
PREFIX dpv: <https://w3id.org/dpv#>
PREFIX dcterm: <http://purl.org/dc/terms/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX adms: <http://www.w3.org/ns/adms#>
PREFIX dcterms: <http://purl.org/dc/terms/>
prefix dc: <http://purl.org/dc/elements/1.1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX : <https://hse.ie/>
PREFIX phi: <https://w3id.org/hse/ontology/phi#>
PREFIX phd: <https://w3id.org/hse/ontology/phd#>
PREFIX pht: <https://w3id.org/hse/terminology#>
PREFIX healthdcatap: <http://healthdata.dublinked.ie/def/healthdcatap#>
"""

def convert_indicator_list_2_str(indicator_list: list[str]) -> str:
  if len(indicator_list) == 0:
     return ""
  indicator_list = list(map(lambda x: f"?indicator = <{x}>", indicator_list))
  return f"FILTER({" || \n".join(indicator_list)})"