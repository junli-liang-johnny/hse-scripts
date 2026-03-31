#!/usr/bin/env python3
"""
Generate a visualization of individual field completeness across all indicators
"""

import argparse
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from SPARQLWrapper import SPARQLWrapper, JSON
    from rdflib import Graph, Namespace
except ImportError as e:
    print(f"Error: Required library not found: {e}", file=sys.stderr)
    print("Install with: pip install matplotlib SPARQLWrapper rdflib", file=sys.stderr)
    sys.exit(1)


# Field definitions with human-readable labels
MANDATORY_FIELDS = [
    ('title', 'Title'),
    ('identifier', 'Indicator ID'),
    ('indicatorType', 'Indicator Type'),
    ('accrualPeriodicity', 'Update Frequency'),
    ('numeratorSource', 'Numerator Source'),
]

RECOMMENDED_FIELDS = [
    ('Rationale', 'Rationale'),
    ('definition', 'Definition'),
    ('status', 'Status'),
    ('numeratorDataElement', 'Numerator Data Element'),
    ('methodology', 'Methodology'),
    ('reportStyle', 'Report Style'),
    ('healthThemeDomain', 'Health Theme Domain'),
    ('healthThemeSubdomain', 'Health Theme Subdomain'),
    ('importance', 'Importance'),
    ('note', 'Note'),
]

OPTIONAL_FIELDS = [
    ('disaggregation', 'Disaggregation'),
    ('denominatorDataElement', 'Denominator Data Element'),
    ('denominatorSource', 'Denominator Source'),
    ('highLowGuidance', 'High/Low Guidance'),
    ('measurementLimitations', 'Measurement Limitations'),
    ('validityGuidance', 'Validity Guidance'),
    ('provenance', 'Provenance'),
    ('historyNote', 'History Note'),
    ('sameAs', 'Same As'),
]

# Indicator fields in the order they appear in indicators.csv
INDICATOR_FIELDS = [
    ('title', 'Title'),
    ('identifier', 'Indicator ID'),
    ('Rationale', 'Rationale'),
    ('definition', 'Definition'),
    ('indicatorType', 'Indicator Type'),
    ('status', 'Status'),
    ('disaggregation', 'Disaggregation'),
    ('numeratorDataElement', 'Numerator Data Element'),
    ('numeratorSource', 'Numerator Source'),
    ('denominatorDataElement', 'Denominator Data Element'),
    ('denominatorSource', 'Denominator Source'),
    ('methodology', 'Methodology'),
    ('accrualPeriodicity', 'Update Frequency'),
    ('reportStyle', 'Report Style'),
    ('healthThemeDomain', 'Health Theme Domain'),
    ('healthThemeSubdomain', 'Health Theme Subdomain'),
    ('highLowGuidance', 'High/Low Guidance'),
    ('measurementLimitations', 'Measurement Limitations'),
    ('validityGuidance', 'Validity Guidance'),
    ('importance', 'Importance'),
    ('provenance', 'Provenance'),
    ('note', 'Note'),
    ('historyNote', 'History Note'),
    ('sameAs', 'Same As'),
]

DATASET_FIELDS = [
    ('datasetTitle', 'Dataset Title'),
    ('datasetIdentifier', 'Dataset ID'),
    ('datasetPublisher', 'Dataset Publisher'),
    ('datasetDescription', 'Dataset Description'),
    ('datasetCreator', 'Dataset Creator'),
    ('datasetStatus', 'Dataset Status'),
    ('datasetProvenance', 'Dataset Provenance'),
    ('datasetContactPoint', 'Contact Point'),
    ('datasetType', 'Dataset Type'),
    ('datasetAccrualPeriodicity', 'Dataset Update Frequency'),
    ('temporalStartDate', 'Temporal Start Date'),
    ('temporalEndDate', 'Temporal End Date'),
    ('temporalResolution', 'Temporal Resolution'),
    ('spatial', 'Spatial Coverage'),
    ('spatialResolutionInMeters', 'Spatial Resolution (Meters)'),
    ('datasetLanguage', 'Language'),
    ('datasetPage', 'Dataset Page'),
    ('accessRights', 'Access Rights'),
    ('datasetComment', 'Comment'),
    ('datasetNote', 'Note'),
    ('hasPersonalData', 'Has Personal Data'),
    ('hasDataController', 'Data Controller'),
    ('hasLegalBasis', 'Legal Basis'),
    ('datasetDistribution', 'Distribution'),
    ('datasetSample', 'Sample Distribution'),
    ('datasetKeyword', 'Keywords'),
    ('datasetTheme', 'Theme'),
    ('applicableLegislation', 'Applicable Legislation'),
    ('hdab', 'Health Data Access Body'),
    ('healthCategory', 'Health Category'),
    ('healthTheme', 'Health Theme'),
    ('conformsTo', 'Conforms To'),
    ('hasCodingScheme', 'Coding Scheme'),
    ('minTypicalAge', 'Min Typical Age'),
    ('maxTypicalAge', 'Max Typical Age'),
    ('populationCoverage', 'Population Coverage'),
    ('inSeries', 'In Series'),
    ('numberOfUniqueIndividuals', 'Number of Unique Individuals'),
    ('SpatialAggregationCode', 'Spatial Aggregation'),
]


def get_field_completeness(sparql_endpoint):
    """Query SPARQL endpoint for field-level completeness"""
    
    sparql = SPARQLWrapper(sparql_endpoint)
    
    query = """
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
PREFIX healthdcatap: <http://healthdata.dublinked.ie/def/healthdcatap#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT
(COUNT(DISTINCT ?indicator) AS ?totalIndicators)
(SUM(IF(BOUND(?title), 1, 0)) AS ?titleCount)
(SUM(IF(BOUND(?identifier), 1, 0)) AS ?identifierCount)
(SUM(IF(BOUND(?indicatorType), 1, 0)) AS ?indicatorTypeCount)
(SUM(IF(BOUND(?accrualPeriodicity), 1, 0)) AS ?accrualPeriodicityCount)
(SUM(IF(BOUND(?numeratorSource), 1, 0)) AS ?numeratorSourceCount)
(SUM(IF(BOUND(?Rationale), 1, 0)) AS ?RationaleCount)
(SUM(IF(BOUND(?definition), 1, 0)) AS ?definitionCount)
(SUM(IF(BOUND(?status), 1, 0)) AS ?statusCount)
(SUM(IF(BOUND(?numeratorDataElement), 1, 0)) AS ?numeratorDataElementCount)
(SUM(IF(BOUND(?methodology), 1, 0)) AS ?methodologyCount)
(SUM(IF(BOUND(?reportStyle), 1, 0)) AS ?reportStyleCount)
(SUM(IF(BOUND(?healthThemeDomain), 1, 0)) AS ?healthThemeDomainCount)
(SUM(IF(BOUND(?healthThemeSubdomain), 1, 0)) AS ?healthThemeSubdomainCount)
(SUM(IF(BOUND(?importance), 1, 0)) AS ?importanceCount)
(SUM(IF(BOUND(?note), 1, 0)) AS ?noteCount)
(SUM(IF(BOUND(?disaggregation), 1, 0)) AS ?disaggregationCount)
(SUM(IF(BOUND(?denominatorDataElement), 1, 0)) AS ?denominatorDataElementCount)
(SUM(IF(BOUND(?denominatorSource), 1, 0)) AS ?denominatorSourceCount)
(SUM(IF(BOUND(?highLowGuidance), 1, 0)) AS ?highLowGuidanceCount)
(SUM(IF(BOUND(?measurementLimitations), 1, 0)) AS ?measurementLimitationsCount)
(SUM(IF(BOUND(?validityGuidance), 1, 0)) AS ?validityGuidanceCount)
(SUM(IF(BOUND(?provenance), 1, 0)) AS ?provenanceCount)
(SUM(IF(BOUND(?historyNote), 1, 0)) AS ?historyNoteCount)
(SUM(IF(BOUND(?sameAs), 1, 0)) AS ?sameAsCount)
(SUM(IF(BOUND(?datasetTitle), 1, 0)) AS ?datasetTitleCount)
(SUM(IF(BOUND(?datasetIdentifier), 1, 0)) AS ?datasetIdentifierCount)
(SUM(IF(BOUND(?datasetPublisher), 1, 0)) AS ?datasetPublisherCount)
(SUM(IF(BOUND(?datasetDescription), 1, 0)) AS ?datasetDescriptionCount)
(SUM(IF(BOUND(?datasetCreator), 1, 0)) AS ?datasetCreatorCount)
(SUM(IF(BOUND(?datasetStatus), 1, 0)) AS ?datasetStatusCount)
(SUM(IF(BOUND(?datasetProvenance), 1, 0)) AS ?datasetProvenanceCount)
(SUM(IF(BOUND(?datasetContactPoint), 1, 0)) AS ?datasetContactPointCount)
(SUM(IF(BOUND(?datasetType), 1, 0)) AS ?datasetTypeCount)
(SUM(IF(BOUND(?datasetAccrualPeriodicity), 1, 0)) AS ?datasetAccrualPeriodicityCount)
(SUM(IF(BOUND(?temporalStartDate), 1, 0)) AS ?temporalStartDateCount)
(SUM(IF(BOUND(?temporalEndDate), 1, 0)) AS ?temporalEndDateCount)
(SUM(IF(BOUND(?temporalResolution), 1, 0)) AS ?temporalResolutionCount)
(SUM(IF(BOUND(?spatial), 1, 0)) AS ?spatialCount)
(SUM(IF(BOUND(?spatialResolutionInMeters), 1, 0)) AS ?spatialResolutionInMetersCount)
(SUM(IF(BOUND(?datasetLanguage), 1, 0)) AS ?datasetLanguageCount)
(SUM(IF(BOUND(?datasetPage), 1, 0)) AS ?datasetPageCount)
(SUM(IF(BOUND(?accessRights), 1, 0)) AS ?accessRightsCount)
(SUM(IF(BOUND(?datasetComment), 1, 0)) AS ?datasetCommentCount)
(SUM(IF(BOUND(?datasetNote), 1, 0)) AS ?datasetNoteCount)
(SUM(IF(BOUND(?hasPersonalData), 1, 0)) AS ?hasPersonalDataCount)
(SUM(IF(BOUND(?hasDataController), 1, 0)) AS ?hasDataControllerCount)
(SUM(IF(BOUND(?hasLegalBasis), 1, 0)) AS ?hasLegalBasisCount)
(SUM(IF(BOUND(?datasetDistribution), 1, 0)) AS ?datasetDistributionCount)
(SUM(IF(BOUND(?datasetSample), 1, 0)) AS ?datasetSampleCount)
(SUM(IF(BOUND(?datasetKeyword), 1, 0)) AS ?datasetKeywordCount)
(SUM(IF(BOUND(?datasetTheme), 1, 0)) AS ?datasetThemeCount)
(SUM(IF(BOUND(?applicableLegislation), 1, 0)) AS ?applicableLegislationCount)
(SUM(IF(BOUND(?hdab), 1, 0)) AS ?hdabCount)
(SUM(IF(BOUND(?healthCategory), 1, 0)) AS ?healthCategoryCount)
(SUM(IF(BOUND(?healthTheme), 1, 0)) AS ?healthThemeCount)
(SUM(IF(BOUND(?conformsTo), 1, 0)) AS ?conformsToCount)
(SUM(IF(BOUND(?hasCodingScheme), 1, 0)) AS ?hasCodingSchemeCount)
(SUM(IF(BOUND(?minTypicalAge), 1, 0)) AS ?minTypicalAgeCount)
(SUM(IF(BOUND(?maxTypicalAge), 1, 0)) AS ?maxTypicalAgeCount)
(SUM(IF(BOUND(?populationCoverage), 1, 0)) AS ?populationCoverageCount)
(SUM(IF(BOUND(?inSeries), 1, 0)) AS ?inSeriesCount)
(SUM(IF(BOUND(?numberOfUniqueIndividuals), 1, 0)) AS ?numberOfUniqueIndividualsCount)
(SUM(IF(BOUND(?SpatialAggregationCode), 1, 0)) AS ?SpatialAggregationCodeCount)
WHERE {
  ?indicator a dcat:Dataset ;
  a phi:Indicator .
  
  OPTIONAL { ?indicator dcterms:title ?title . }
  OPTIONAL { ?indicator dct:identifier ?identifier }
  OPTIONAL { ?indicator phi:indicatorType ?indicatorType . }
  OPTIONAL { ?indicator dcterms:accrualPeriodicity ?accrualPeriodicity . }
  OPTIONAL { 
    ?indicator phi:numeratorSource ?numeratorSource .
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:title ?datasetTitle . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dct:identifier ?datasetIdentifier . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dct:publisher ?datasetPublisher . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:description ?datasetDescription . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:creator ?datasetCreator . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; hwbp:status ?datasetStatus . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dct:Provenance ?datasetProvenance . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcat:contactPoint ?datasetContactPoint . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:type ?datasetType . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:accrualPeriodicity ?datasetAccrualPeriodicity . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:temporal/dcat:startDate ?temporalStartDate . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:temporal/dcat:endDate ?temporalEndDate . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcat:temporalResolution ?temporalResolution . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dc:spatial ?spatial . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcat:spatialResolutionInMeters ?spatialResolutionInMeters . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:language ?datasetLanguage . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; foaf:page ?datasetPage . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcterms:accessRights ?accessRights . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; rdfs:comment ?datasetComment . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; skos:note ?datasetNote . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dpv:hasPersonalData ?hasPersonalData . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dpv:hasDataController ?hasDataController . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dpv:hasLegalBasis ?hasLegalBasis . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcat:distribution ?datasetDistribution . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; adms:sample ?datasetSample . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcat:keyword ?datasetKeyword . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcat:theme ?datasetTheme . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcatsp:applicableLegislation ?applicableLegislation . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; healthdcatap:hdab ?hdab . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; healthdcatap:healthCategory ?healthCategory . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; healthdcatap:healthTheme ?healthTheme . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dc:conformsTo ?conformsTo . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; hwbp:hasCodingScheme ?hasCodingScheme . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; healthdcatap:minTypicalAge ?minTypicalAge . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; healthdcatap:maxTypicalAge ?maxTypicalAge . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; healthdcatap:populationCoverage ?populationCoverage . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; dcat:inSeries ?inSeries . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; healthdcatap:numberOfUniqueIndividuals ?numberOfUniqueIndividuals . }
    OPTIONAL { ?numeratorSource a dcat:Dataset ; phd:spatialAggregation ?SpatialAggregationCode . }
  }
  OPTIONAL { ?indicator phi:Rationale ?Rationale . }
  OPTIONAL { ?indicator skos:definition ?definition . }
  OPTIONAL { ?indicator phi:status ?status . }
  OPTIONAL { ?indicator phi:numeratorDataElement ?numeratorDataElement . }
  OPTIONAL { ?indicator phi:methodology ?methodology . }
  OPTIONAL { ?indicator phi:reportStyle ?reportStyle . }
  OPTIONAL { ?indicator healthdcatap:healthTheme ?healthThemeDomain . 
    ?healthThemeDomain a healthdcatap:Domain . 
  }
  OPTIONAL { ?indicator healthdcatap:healthTheme ?healthThemeSubdomain . 
    ?healthThemeSubdomain a healthdcatap:Subdomain . 
  }
  OPTIONAL { ?indicator phi:importance ?importance . }
  OPTIONAL { ?indicator skos:note ?note . }
  OPTIONAL { ?indicator phi:disaggregation ?disaggregation . }
  OPTIONAL { ?indicator phi:denominatorDataElement ?denominatorDataElement . }
  OPTIONAL { ?indicator phi:denominatorSource ?denominatorSource . }
  OPTIONAL { ?indicator phi:highLowGuidance ?highLowGuidance . }
  OPTIONAL { ?indicator phi:measurementLimitations ?measurementLimitations . }
  OPTIONAL { ?indicator phi:validityGuidance ?validityGuidance . }
  OPTIONAL { ?indicator dct:provenance ?provenance . }
  OPTIONAL { ?indicator skos:historyNote ?historyNote . }
  OPTIONAL { ?indicator owl:sameAs ?sameAs . }
}
"""
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    bindings = results["results"]["bindings"][0]
    total = int(bindings["totalIndicators"]["value"])
    
    # Extract counts for each field
    field_data = {}
    all_fields = MANDATORY_FIELDS + RECOMMENDED_FIELDS + OPTIONAL_FIELDS + DATASET_FIELDS
    
    for field_key, field_label in all_fields:
        count_key = f"{field_key}Count"
        count = int(bindings[count_key]["value"])
        percentage = (count / total * 100) if total > 0 else 0
        field_data[field_key] = {
            'label': field_label,
            'count': count,
            'percentage': percentage,
            'total': total
        }
    
    return field_data, total


def get_field_completeness_from_file(ttl_file):
    """Query local TTL file for field-level completeness"""
    
    print(f"Loading RDF graph from: {ttl_file}")
    g = Graph()
    g.parse(ttl_file, format='turtle')
    print(f"✓ Loaded {len(g)} triples")
    
    # Define namespaces
    DCAT = Namespace("http://www.w3.org/ns/dcat#")
    DCTERMS = Namespace("http://purl.org/dc/terms/")
    DCT = Namespace("http://purl.org/dc/terms/")
    DC = Namespace("http://purl.org/dc/elements/1.1/")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    ADMS = Namespace("http://www.w3.org/ns/adms#")
    DCATSP = Namespace("http://data.europa.eu/w21/016d88c3-a723-4111-aae2-768c78e5e58f#")
    HWBP = Namespace("https://www.w3.org/ns/dx/prof/")
    PHI = Namespace("https://w3id.org/hse/ontology/phi#")
    PHD = Namespace("https://w3id.org/hse/ontology/phd#")
    HEALTHDCATAP = Namespace("http://healthdata.dublinked.ie/def/healthdcatap#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    DPV = Namespace("https://w3id.org/dpv#")
    
    # Get all indicators
    indicators = list(g.subjects(predicate=None, object=PHI.Indicator))
    total = len(indicators)
    
    print(f"Found {total} indicators")
    
    # Initialize counters
    field_counts = {
        'title': 0,
        'identifier': 0,
        'indicatorType': 0,
        'accrualPeriodicity': 0,
        'numeratorSource': 0,
        'Rationale': 0,
        'definition': 0,
        'status': 0,
        'numeratorDataElement': 0,
        'methodology': 0,
        'reportStyle': 0,
        'healthThemeDomain': 0,
        'healthThemeSubdomain': 0,
        'importance': 0,
        'note': 0,
        'disaggregation': 0,
        'denominatorDataElement': 0,
        'denominatorSource': 0,
        'highLowGuidance': 0,
        'measurementLimitations': 0,
        'validityGuidance': 0,
        'provenance': 0,
        'historyNote': 0,
        'sameAs': 0,
        'datasetTitle': 0,
        'datasetIdentifier': 0,
        'datasetPublisher': 0,
        'datasetDescription': 0,
        'datasetCreator': 0,
        'datasetStatus': 0,
        'datasetProvenance': 0,
        'datasetContactPoint': 0,
        'datasetType': 0,
        'datasetAccrualPeriodicity': 0,
        'temporalStartDate': 0,
        'temporalEndDate': 0,
        'temporalResolution': 0,
        'spatial': 0,
        'spatialResolutionInMeters': 0,
        'datasetLanguage': 0,
        'datasetPage': 0,
        'accessRights': 0,
        'datasetComment': 0,
        'datasetNote': 0,
        'hasPersonalData': 0,
        'hasDataController': 0,
        'hasLegalBasis': 0,
        'datasetDistribution': 0,
        'datasetSample': 0,
        'datasetKeyword': 0,
        'datasetTheme': 0,
        'applicableLegislation': 0,
        'hdab': 0,
        'healthCategory': 0,
        'healthTheme': 0,
        'conformsTo': 0,
        'hasCodingScheme': 0,
        'minTypicalAge': 0,
        'maxTypicalAge': 0,
        'populationCoverage': 0,
        'inSeries': 0,
        'numberOfUniqueIndividuals': 0,
        'SpatialAggregationCode': 0,
        'datasetDistribution': 0,
    }
    
    # Count field presence for each indicator
    for indicator in indicators:
        # Mandatory fields
        if g.value(indicator, DCTERMS.title):
            field_counts['title'] += 1
        if g.value(indicator, DCT.identifier):
            field_counts['identifier'] += 1
        if g.value(indicator, PHI.indicatorType):
            field_counts['indicatorType'] += 1
        if g.value(indicator, DCTERMS.accrualPeriodicity):
            field_counts['accrualPeriodicity'] += 1
        
        numerator_source = g.value(indicator, PHI.numeratorSource)
        if numerator_source:
            field_counts['numeratorSource'] += 1
            # Check dataset fields
            if g.value(numerator_source, DCTERMS.title):
                field_counts['datasetTitle'] += 1
            if g.value(numerator_source, DCT.identifier):
                field_counts['datasetIdentifier'] += 1
            if g.value(numerator_source, DCT.publisher):
                field_counts['datasetPublisher'] += 1
            if g.value(numerator_source, DCTERMS.description):
                field_counts['datasetDescription'] += 1
            if g.value(numerator_source, DCTERMS.creator):
                field_counts['datasetCreator'] += 1
            if g.value(numerator_source, HWBP.status):
                field_counts['datasetStatus'] += 1
            if g.value(numerator_source, DCT.Provenance):
                field_counts['datasetProvenance'] += 1
            if g.value(numerator_source, DCAT.contactPoint):
                field_counts['datasetContactPoint'] += 1
            if g.value(numerator_source, DCTERMS.type):
                field_counts['datasetType'] += 1
            if g.value(numerator_source, DCTERMS.accrualPeriodicity):
                field_counts['datasetAccrualPeriodicity'] += 1
            # Check temporal properties - look for temporal with start/end dates
            for temporal in g.objects(numerator_source, DCTERMS.temporal):
                if g.value(temporal, DCAT.startDate):
                    field_counts['temporalStartDate'] += 1
                if g.value(temporal, DCAT.endDate):
                    field_counts['temporalEndDate'] += 1
            if g.value(numerator_source, DCAT.temporalResolution):
                field_counts['temporalResolution'] += 1
            if g.value(numerator_source, DC.spatial):
                field_counts['spatial'] += 1
            if g.value(numerator_source, DCAT.spatialResolutionInMeters):
                field_counts['spatialResolutionInMeters'] += 1
            if g.value(numerator_source, DCTERMS.language):
                field_counts['datasetLanguage'] += 1
            if g.value(numerator_source, FOAF.page):
                field_counts['datasetPage'] += 1
            if g.value(numerator_source, DCTERMS.accessRights):
                field_counts['accessRights'] += 1
            if g.value(numerator_source, RDFS.comment):
                field_counts['datasetComment'] += 1
            if g.value(numerator_source, SKOS.note):
                field_counts['datasetNote'] += 1
            if g.value(numerator_source, DPV.hasPersonalData):
                field_counts['hasPersonalData'] += 1
            if g.value(numerator_source, DPV.hasDataController):
                field_counts['hasDataController'] += 1
            if g.value(numerator_source, DPV.hasLegalBasis):
                field_counts['hasLegalBasis'] += 1
            if g.value(numerator_source, DCAT.distribution):
                field_counts['datasetDistribution'] += 1
            if g.value(numerator_source, ADMS.sample):
                field_counts['datasetSample'] += 1
            if g.value(numerator_source, DCAT.keyword):
                field_counts['datasetKeyword'] += 1
            if g.value(numerator_source, DCAT.theme):
                field_counts['datasetTheme'] += 1
            if g.value(numerator_source, DCATSP.applicableLegislation):
                field_counts['applicableLegislation'] += 1
            if g.value(numerator_source, HEALTHDCATAP.hdab):
                field_counts['hdab'] += 1
            if g.value(numerator_source, HEALTHDCATAP.healthCategory):
                field_counts['healthCategory'] += 1
            if g.value(numerator_source, HEALTHDCATAP.healthTheme):
                field_counts['healthTheme'] += 1
            if g.value(numerator_source, DC.conformsTo):
                field_counts['conformsTo'] += 1
            if g.value(numerator_source, HWBP.hasCodingScheme):
                field_counts['hasCodingScheme'] += 1
            if g.value(numerator_source, HEALTHDCATAP.minTypicalAge):
                field_counts['minTypicalAge'] += 1
            if g.value(numerator_source, HEALTHDCATAP.maxTypicalAge):
                field_counts['maxTypicalAge'] += 1
            if g.value(numerator_source, HEALTHDCATAP.populationCoverage):
                field_counts['populationCoverage'] += 1
            if g.value(numerator_source, DCAT.inSeries):
                field_counts['inSeries'] += 1
            if g.value(numerator_source, HEALTHDCATAP.numberOfUniqueIndividuals):
                field_counts['numberOfUniqueIndividuals'] += 1
            if g.value(numerator_source, PHD.spatialAggregation):
                field_counts['SpatialAggregationCode'] += 1
        
        # Recommended fields
        if g.value(indicator, PHI.Rationale):
            field_counts['Rationale'] += 1
        if g.value(indicator, SKOS.definition):
            field_counts['definition'] += 1
        if g.value(indicator, PHI.status):
            field_counts['status'] += 1
        if g.value(indicator, PHI.numeratorDataElement):
            field_counts['numeratorDataElement'] += 1
        if g.value(indicator, PHI.methodology):
            field_counts['methodology'] += 1
        if g.value(indicator, PHI.reportStyle):
            field_counts['reportStyle'] += 1
        
        # Check for health theme domain
        for theme in g.objects(indicator, HEALTHDCATAP.healthTheme):
            if (theme, None, HEALTHDCATAP.Domain) in g:
                field_counts['healthThemeDomain'] += 1
                break
        
        # Check for health theme subdomain
        for theme in g.objects(indicator, HEALTHDCATAP.healthTheme):
            if (theme, None, HEALTHDCATAP.Subdomain) in g:
                field_counts['healthThemeSubdomain'] += 1
                break
        
        if g.value(indicator, PHI.importance):
            field_counts['importance'] += 1
        if g.value(indicator, SKOS.note):
            field_counts['note'] += 1
        
        # Optional fields
        if g.value(indicator, PHI.disaggregation):
            field_counts['disaggregation'] += 1
        if g.value(indicator, PHI.denominatorDataElement):
            field_counts['denominatorDataElement'] += 1
        if g.value(indicator, PHI.denominatorSource):
            field_counts['denominatorSource'] += 1
        if g.value(indicator, PHI.highLowGuidance):
            field_counts['highLowGuidance'] += 1
        if g.value(indicator, PHI.measurementLimitations):
            field_counts['measurementLimitations'] += 1
        if g.value(indicator, PHI.validityGuidance):
            field_counts['validityGuidance'] += 1
        if g.value(indicator, DCT.provenance):
            field_counts['provenance'] += 1
        if g.value(indicator, SKOS.historyNote):
            field_counts['historyNote'] += 1
        if g.value(indicator, OWL.sameAs):
            field_counts['sameAs'] += 1
    
    # Build field data dictionary
    field_data = {}
    all_fields = MANDATORY_FIELDS + RECOMMENDED_FIELDS + OPTIONAL_FIELDS + DATASET_FIELDS
    
    for field_key, field_label in all_fields:
        count = field_counts[field_key]
        percentage = (count / total * 100) if total > 0 else 0
        field_data[field_key] = {
            'label': field_label,
            'count': count,
            'percentage': percentage,
            'total': total
        }
    
    return field_data, total


def visualize_field_completeness(field_data, total_indicators, output_file=None, field_type='all', horizontal=False):
    """Generate bar chart visualization of per-field completeness"""
    
    # Select fields based on type
    if field_type == 'mandatory':
        selected_fields = MANDATORY_FIELDS
        title_suffix = '(Mandatory Fields)'
    elif field_type == 'recommended':
        selected_fields = RECOMMENDED_FIELDS
        title_suffix = '(Recommended Fields)'
    elif field_type == 'optional':
        selected_fields = OPTIONAL_FIELDS
        title_suffix = '(Optional Fields)'
    elif field_type == 'indicator':
        selected_fields = INDICATOR_FIELDS
        title_suffix = '(Indicator Fields)'
    elif field_type == 'dataset':
        selected_fields = DATASET_FIELDS
        title_suffix = '(Dataset Fields)'
    else:  # all
        selected_fields = MANDATORY_FIELDS + RECOMMENDED_FIELDS + OPTIONAL_FIELDS + DATASET_FIELDS
        title_suffix = ''
    
    field_labels = []
    counts = []
    percentages = []
    
    for field_key, field_label in selected_fields:
        data = field_data[field_key]
        field_labels.append(field_label)
        counts.append(data['count'])
        percentages.append(data['percentage'])
    
    # Reverse order for horizontal charts so first item appears at top
    if horizontal:
        field_labels = field_labels[::-1]
        counts = counts[::-1]
        percentages = percentages[::-1]
    
    if horizontal:
        # Create horizontal bar chart
        fig, ax1 = plt.subplots(figsize=(12, max(8, len(field_labels) * 0.5)))
        
        # Set up y-axis
        y = range(len(field_labels))
        height = 0.35
        
        # Plot counts (blue bars)
        bars1 = ax1.barh([i - height/2 for i in y], counts, height, label='Count', color='#3498db', alpha=0.8)
        
        # Set axis labels based on field type
        y_label = 'Dataset Fields' if field_type == 'dataset' else 'Indicator Fields'
        x_label = 'Number of Datasets' if field_type == 'dataset' else 'Number of Indicators'
        
        ax1.set_ylabel(y_label, fontsize=12, fontweight='bold')
        ax1.set_xlabel(x_label, fontsize=12, fontweight='bold', color='#3498db')
        ax1.tick_params(axis='x', labelcolor='#3498db')
        ax1.set_xlim(0, total_indicators * 1.1)
        
        # Create second x-axis for percentages
        ax2 = ax1.twiny()
        bars2 = ax2.barh([i + height/2 for i in y], percentages, height, label='Percentage', color='#f39c12', alpha=0.8)
        ax2.set_xlabel('Completeness Percentage (%)', fontsize=12, fontweight='bold', color='#f39c12')
        ax2.tick_params(axis='x', labelcolor='#f39c12')
        ax2.set_xlim(0, 110)
        
        # Set y-axis labels
        ax1.set_yticks(y)
        ax1.set_yticklabels(field_labels, fontsize=10)
        
        # Add value labels on bars
        for bar, count in zip(bars1, counts):
            width_val = bar.get_width()
            ax1.text(width_val, bar.get_y() + bar.get_height()/2.,
                    f' {count}',
                    ha='left', va='center', fontsize=9, color='#2c3e50')
        
        for bar, pct in zip(bars2, percentages):
            width_val = bar.get_width()
            ax2.text(width_val, bar.get_y() + bar.get_height()/2.,
                    f' {pct:.1f}%',
                    ha='left', va='center', fontsize=9, color='#e67e22')
        
        # Add grid for better readability
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        
    else:
        # Create vertical bar chart
        fig, ax1 = plt.subplots(figsize=(16, 8))
        
        # Set up x-axis
        x = range(len(field_labels))
        width = 0.35
        
        # Plot counts (blue bars)
        bars1 = ax1.bar([i - width/2 for i in x], counts, width, label='Count', color='#3498db', alpha=0.8)
        ax1.set_xlabel('Indicator Fields', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Number of Indicators', fontsize=12, fontweight='bold', color='#3498db')
        ax1.tick_params(axis='y', labelcolor='#3498db')
        ax1.set_ylim(0, total_indicators * 1.1)
        
        # Create second y-axis for percentages
        ax2 = ax1.twinx()
        bars2 = ax2.bar([i + width/2 for i in x], percentages, width, label='Percentage', color='#f39c12', alpha=0.8)
        ax2.set_ylabel('Completeness Percentage (%)', fontsize=12, fontweight='bold', color='#f39c12')
        ax2.tick_params(axis='y', labelcolor='#f39c12')
        ax2.set_ylim(0, 110)
        
        # Set x-axis labels
        ax1.set_xticks(x)
        ax1.set_xticklabels(field_labels, rotation=45, ha='right', fontsize=9)
        
        # Add value labels on bars
        for bar, count in zip(bars1, counts):
            height_val = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height_val,
                    f'{count}',
                    ha='center', va='bottom', fontsize=8, color='#2c3e50')
        
        for bar, pct in zip(bars2, percentages):
            height_val = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height_val,
                    f'{pct:.1f}%',
                    ha='center', va='bottom', fontsize=8, color='#e67e22')
        
        # Add grid for better readability
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add title
    plt.title(f'Individual Field Completeness Summary {title_suffix}\n(n={total_indicators} indicators)', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Create custom legend
    blue_patch = mpatches.Patch(color='#3498db', label='Count (blue)', alpha=0.8)
    yellow_patch = mpatches.Patch(color='#f39c12', label='Percentage (yellow)', alpha=0.8)
    ax1.legend(handles=[blue_patch, yellow_patch], loc='best', fontsize=10)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Visualization saved to: {output_file}")
    else:
        print("\n✓ Displaying visualization...")
        plt.show()
    
    plt.close()


def main():
    """CLI entry point"""
    script_dir = Path(__file__).parent
    default_output = script_dir.parent.parent.parent / "hse-data" / "output" / "dq" / "v10" / "field_completeness_chart.png"
    default_ttl = script_dir.parent.parent.parent / "hse-data" / "mapping" / "v10" / "mappings_final.ttl"
    
    parser = argparse.ArgumentParser(
        description='Generate visualization of individual field completeness across all indicators',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use default TTL file (v10)
  hse-field-viz --save-default
  
  # Use custom TTL file
  hse-field-viz -f /path/to/mappings.ttl -o output.png
  
  # Use SPARQL endpoint
  hse-field-viz -e http://localhost:3030/v10
  
  # Show only mandatory fields from TTL file
  hse-field-viz -f mappings.ttl --type mandatory
  
  # Show only recommended fields from endpoint
  hse-field-viz -e http://localhost:3030/v10 --type recommended --save-default
  
  # Show all indicator fields in indicators.csv order with horizontal layout
  hse-field-viz --type indicator --horizontal --save-default
  
  # Show dataset fields in horizontal layout
  hse-field-viz --type dataset --horizontal
        '''
    )
    
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        '-e', '--endpoint',
        help='SPARQL endpoint URL (e.g., http://localhost:3030/v10)'
    )
    
    source_group.add_argument(
        '-f', '--file',
        help=f'Path to TTL/RDF file (default: {default_ttl.name} in v10)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output file path for the chart (PNG format). If not specified, chart will be displayed.'
    )
    
    parser.add_argument(
        '--save-default',
        action='store_true',
        help=f'Save to default location: {default_output}'
    )
    
    parser.add_argument(
        '--type',
        choices=['all', 'mandatory', 'recommended', 'optional', 'indicator', 'dataset'],
        default='all',
        help='Type of fields to display (default: all)'
    )
    
    parser.add_argument(
        '--horizontal',
        action='store_true',
        help='Display as horizontal bar chart (fields on y-axis)'
    )
    
    args = parser.parse_args()
    
    # Determine data source
    if args.endpoint:
        print(f"Querying SPARQL endpoint: {args.endpoint}")
        try:
            field_data, total_indicators = get_field_completeness(args.endpoint)
        except Exception as e:
            print(f"Error querying SPARQL endpoint: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        ttl_file = Path(args.file)
        if not ttl_file.exists():
            print(f"Error: File not found: {ttl_file}", file=sys.stderr)
            sys.exit(1)
        try:
            field_data, total_indicators = get_field_completeness_from_file(ttl_file)
        except Exception as e:
            print(f"Error reading TTL file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Use default TTL file
        if not default_ttl.exists():
            print(f"Error: Default TTL file not found: {default_ttl}", file=sys.stderr)
            print("Please specify a data source with -e or -f", file=sys.stderr)
            sys.exit(1)
        print(f"Using default TTL file: {default_ttl}")
        try:
            field_data, total_indicators = get_field_completeness_from_file(default_ttl)
        except Exception as e:
            print(f"Error reading default TTL file: {e}", file=sys.stderr)
            sys.exit(1)
    
    output_file = None
    if args.save_default:
        output_file = default_output
        output_file.parent.mkdir(parents=True, exist_ok=True)
    elif args.output:
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    
    visualize_field_completeness(field_data, total_indicators, output_file, args.type, args.horizontal)


if __name__ == "__main__":
    main()
