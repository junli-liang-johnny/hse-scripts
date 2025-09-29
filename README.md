# HSE Data Pipeline Scripts

## Overview

This repository contains a comprehensive data pipeline for converting raw CSV files into RDF (Resource Description Framework) data in TTL (Turtle) format. The pipeline is specifically designed for processing HSE and CSO data, including indicators and datasets, with the goal of creating semantic web-ready data that follows established ontologies and vocabularies.

## Pipeline Purpose

The main objective of this pipeline is to:

- **Transform raw CSV data** into semantically structured RDF data
- **Clean and standardize** input data through various preprocessing steps
- **Populate missing data** where appropriate using inference and mapping rules
- **Generate compliant RDF** that adheres to DCAT (Data Catalog Vocabulary), Dublin Core, and other relevant ontologies
- **Produce high-quality linked data** suitable for semantic web applications and SPARQL querying

## Pipeline Architecture

The pipeline follows a multi-stage approach:

1. **Data Ingestion**: Raw CSV files are processed and cleaned
2. **Data Preparation**: CSV files are converted to RDF-ready format with proper column mappings
3. **Entity Creation**: Separate CSV files are created for different RDF entities (datasets, publishers, provenance, etc.)
4. **Subject Identification**: Unique identifiers are added to create proper RDF subjects
5. **RDF Mapping**: CSV data is mapped to RDF using RML (RDF Mapping Language)
6. **Data Refinement**: Unnecessary triples are removed and data transformations are applied
7. **Output Generation**: Final TTL files are produced for consumption

## Data Processing Features

- **Data Cleaning**: Standardization of column names, data types, and formats
- **Missing Data Handling**: Intelligent population of missing values based on context and rules
- **Entity Resolution**: Creation of unique identifiers for entities across different data sources
- **Namespace Management**: Consistent use of namespaces for proper RDF structure
- **Validation**: Built-in validation steps to ensure data quality and compliance

## Output Format

The pipeline generates RDF data in Turtle (TTL) format that includes:

- Properly structured triples following semantic web standards
- Links between related entities (datasets, publishers, indicators)
- Metadata enrichment using standard vocabularies
- SPARQL-queryable data for advanced analytics and reporting

## Dependencies

The pipeline requires several Python packages (see `requirements.txt`) and follows modular design principles for maintainability and extensibility.

## Data Sources

**Note**: The raw CSV datasets used in this pipeline contain sensitive health data and are stored in a separate private repository for security and privacy compliance. The pipeline scripts in this repository are designed to work with these datasets once they are made available in the appropriate data directories.

## Namespacing

```
PREFIX : <https://hse.ie/>
PREFIX phi: <https://hse.ie/ontology/phi#>
PREFIX phd: <https://hse.ie/ontology/phd#>
PREFIX phpt: <https://hse.ie/ontology/phpt#>
```

## Metadata Fields

### Indicators Metadata Fields

#### Mandatory Fields

```
dcterms:title
dct:identifier
phi:indicatorType
phi:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]
dcterms:accrualPeriodicity
```

#### Recommended Fields

```
phi:Rationale
skos:definition
phi:status
phi:disaggregation
phi:numeratorDataElement
healthdcatap:healthTheme (domain)
healthdcatap:healthTheme (subdomain)
dct:provenance [a dct:ProvenanceStatement; rdfs:label ]
skos:note
```

#### Optional Fields

```
phi:denominatorDataElement
phi:denominatorSource [a dct:dataset [a dct:publisher [a dcterms:source]]]
phi:methodology
phi:highLowGuidance
phi:measurementLimitations
phi:validityGuidance
skos:historyNote
```

### Datasets Metadata Fields

#### Mandatory Fields

```
dcterms:title
dct:identifier
dct:publisher [ a dct:Publisher; foaf:name ]
dcterms:description
dct:Provenance [a dct:ProvenanceStatement; rdfs:label ]
dcat:contactPoint [vcard:individual vard:fn]
dcterms:type
dc:spatial
dcterms:accessRights
dcat:distribution [ a dcat:Distribution; dct:format]
adms:sample[ a dcat:Distribution; dcat:accessURL]
dcat:keyword
dcat:theme
dcatsp:applicableLegislation
dct:type
healthdcatap:hdab [a foaf:Agent;  foaf:name ]
healthdcatap:healthCategory
healthdcatap:healthTheme
```

### Recommended Fields

```
dcterms:accrualPeriodicity
dcterms:temporal [a dct:PeriodOfTime;  dcat:startDate ""^^xsd:dateTime; dcat:endDate ""^^xsd:dateTime.]
dcterms:temporal [a dct:PeriodOfTime;  dcat:endDate ""^^xsd:dateTime.]
dcat:temporalResolution
dcterms:language
dpv:hasPersonalData
dpv:hasLegalBasis
dc:conformsTo
healthdcatap:minTypicalAge
healthdcatap:maxTypicalAge
```

### Optional Fields

```
dcterms:creator
phd:status
dcat:spatialResolutionInMeters
foaf:page
rdfs:comment
skos:note
dpv:hasDataController
healthdcatap:populationCoverage
dcat:inSeries
healthdcatap:numberOfUniqueIndividuals
skos:note
```

---

## Pipeline steps for Indicators

### 1. convert original csv to rdf-ready csv (data cleaning)

```
python -m scripts.rdf_mapping.csv_rdf_convert \
 --input ./data/cso/combined_indicators.csv \
 --output ./mapping/indicators.csv
```

### 2. create indicators dcat datasets

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/indicators.csv \
 --output ./mapping/indicators_dcat-dataset.csv \
 --column 'hwbp:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
 --header 'id' 'rdf:type' 'dcterms:publisher' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/dataset/{uuid}' \
 --extracted-value-insert-index -1 \
 --optional-values-to-insert 'dcat:Dataset' 'https://hse-oahwb-profile.adaptcentre.ie/publisher/{uuid}'
```

### 3. create indicators publishers

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/indicators.csv \
 --output ./mapping/indicators_publishers.csv \
 --column 'hwbp:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
 --header 'id' 'rdf:type' 'dcterms:source' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/publisher/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:Publisher' \
 --identifier-csv ./mapping/indicators_dcat-dataset.csv \
 --identifier-column dcterms:publisher
```

### 4. create indicators provenance

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/indicators.csv \
 --output ./mapping/indicators_provenance.csv \
 --column 'dct:provenance [a dct:ProvenanceStatement; rdfs:label ]' \
 --header 'id' 'rdf:type' 'rdfs:label' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/provenance/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcterms:ProvenanceStatement'
```

### 5. add id to rows in csv

```
python -m scripts.rdf_mapping.create_subject_csv \
 --input ./mapping/indicators.csv \
 --output ./mapping/indicators_final.csv \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie/indicator/' \
 --id-template-column 'dct:identifier'
```

### 6. use rml-py to map csv to rdf

```
python -m scripts.rdf_mapping.map_to_rdf --config ./mapping/config.ttl
```

### 7. delete unnecessary triples

```
python -m sparql.run_query \
	--ttl-file ./mapping/indicators.ttl \
	--query-file sparql/general_transfer.rq \
	--output ./mapping/indicators_final.ttl
```

## Pipeline steps for datasets

### 1. convert original csv to rdf-ready csv (data cleaning)

```
csv-rdf-convert \
 --input ../hse-data/data/schema/OAHP_MasterDataCatalogueVersion0007.xlsx\ -\ Datasets.csv \
 --output ../hse-data/mapping/v7/datasets.csv
```

### 2. create datasets' publisher

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_publishers.csv \
 --column 'dct:publisher [ a dct:Publisher; foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:Publisher' \
 --identifier-csv ../hse-data/mapping/v7/datasets.csv \
 --identifier-column 'dct:publisher [ a dct:Publisher; foaf:name ]'
```

### 4. create datasets provenance

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_provenance.csv \
 --column 'dct:Provenance [a dct:ProvenanceStatement; rdfs:label ]' \
 --header 'id' 'rdf:type' 'rdfs:label' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcterms:ProvenanceStatement'
```

### 5. create datasets contact point

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_contact_point.csv \
 --column 'dcat:contactPoint [vcard:individual vard:fn]' \
 --header 'id' 'rdf:type' 'vcard:fn' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'vcard:Individual'
```

### 6. create datasets Data Coverage Start Date

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_data_coverage_start_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime;  dcat:startDate """"^^xsd:dateTime; dcat:endDate """"^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:startDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'
```

### 7. create datasets Data Coverage End Date

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_data_coverage_end_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:endDate "^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:endDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'
```

### 8. create datasets distributions

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_distributions.csv \
 --column 'dcat:distribution [ a dcat:Distribution; dct:format]' \
 --header 'id' 'rdf:type' 'dct:format' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'
```

### 9. create datasets adms:sample

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_adms_sample.csv \
 --column 'adms:sample[ a dcat:Distribution; dcat:accessURL]' \
 --header 'id' 'rdf:type' 'dcat:accessURL' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'
```

### 10. create datasets healthdcatap:hdab

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_healthdcatap:hdab.csv \
 --column 'healthdcatap:hdab [a foaf:Agent;  foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'foaf:Agent'
```

### 5. add id to rows in csv

```
<!-- create-subject-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_final.csv \
 --namespace 'https://hse.id' \
	--id-template '/data/id/{uuid}' \
 --id-template-column 'dct:identifier' \
 --split-by "/" \
 --template-split-index -1 -->

create-subject-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_final.csv \
 --namespace 'https://hse.ie/data/id/' \
 --id-template-column 'dct:identifier'
```

### 6. use rml-py to map csv to rdf

```
map2rdf --config ../hse-data/mapping/v7/config.ttl
```

### 7. delete unnecessary triples

```
python -m sparql.run_query \
	--ttl-file ./mapping/datasets.ttl \
	--query-file sparql/general_transfer.rq \
	--output ./mapping/datasets_final.ttl
```

### 8. data transformation

"dpv:NonPersonalData" -> dpv:NonPersonalData

```
python -m sparql.run_query \
	--ttl-file ./mapping/datasets.ttl \
	--query-file ./sparql/datasets_transfer.rq \
	--output ./datasets_final.ttl
```

## Pipeline - combine delphi input with cso indicator master list

### 1. Join - quite specific to the input files recevied from HSE

```
hse-data-join \
	--delphi data/final-delphi.csv \
	--master data/final-delphi-master \
	--on "SORT CODE" \
	--output output/joined.csv
```

### 2. Add columns - combine delphi and cso indicators

```
hse-add-columns \
	--primary data/combined_indicators.csv \
	--secondary output/joined.csv \
	--output output/joined_combined.csv \
```

### 3. Re order headers - move indicator's headers to front followed by delphi's ones

```
hse-re-order \
	--input output/joined_combined.csv \
	--output output/reordered.csv \
	--move-to-front "Status (included or 'maybe included')"
```

### 4. Add subheaders (rdf headers and MRO)

```
hse-add-subheaders \
	--input output/reordered.csv \
	--output output/sub_headers_added.csv \
	--subheaders dcterms:title dct:identifier hwbp:Rationale skos:definition hwbp:indicatorType hwbp:status hwbp:disaggregation hwbp:numeratorDataElement "hwbp:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]" hwbp:denominatorDataElement "hwbp:denominatorSource [a dct:dataset [a dct:publisher [a dcterms:source]]" hwbp:methodology dcterms:accrualPeriodicity hwbp:reportStyle healthdcatap:healthTheme healthdcatap:healthTheme hwbp:highLowGuidance hwbp:measurementLimitations hwbp:validityGuidance hwbp:importance "dct:provenance [a dct:ProvenanceStatement; rdfs:label ]" skos:note \
	--start-column-index 1

hse-add-subheaders \
	--input output/sub_headers_added.csv \
	--output output/final.csv \
	--subheaders M M R R M R O R M O O R M R R R O O O R O R \
	--start-column-index 1 \
	--start-row-index 1 \
	--fill-value not_set
```

## Convert Delphi input into RDF V.5

### 1. convert original csv to rdf-ready csv (data cleaning)

```
csv-rdf-convert \
	--input ../hse-data/data/schema/OAHP_MasterDataCatalogueVersion0005.xlsx - Indicators.csv \
	--output ../hse-data/mapping/v5/indicators_v5.csv
```

### 2. create indicators dcat datasets

```
create-csv \
	--input ../hse-data/mapping/v5/indicators_v5.csv \
	--output ../hse-data/mapping/v5/indicators_dcat-dataset_v5.csv \
	--column 'hwbp:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
	--header 'id' 'rdf:type' 'dcterms:publisher' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index -1 \
	--optional-values-to-insert 'dcat:Dataset' 'https://hse.ie/data/id/{uuid}'
```

### 3. create indicators publishers

```
create-csv \
	--input ../hse-data/mapping/v5/indicators_v5.csv \
	--output ../hse-data/mapping/v5/indicators_publishers_v5.csv \
	--column 'hwbp:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
	--header 'id' 'rdf:type' 'dcterms:source' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index 2 \
	--optional-values-to-insert 'dct:Publisher' \
	--identifier-csv ../hse-data/mapping/indicators_dcat-dataset.csv \
	--identifier-column dcterms:publisher
```

### 4. create indicators provenance

```
create-csv \
	--input ../hse-data/mapping/v5/indicators_v5.csv \
	--output ../hse-data/mapping/v5/indicators_provenance_v5.csv \
	--column 'dct:provenance [a dct:ProvenanceStatement;rdfs:label ]' \
	--header 'id' 'rdf:type' 'rdfs:label' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index 2 \
	--optional-values-to-insert 'dcterms:ProvenanceStatement'
```

### 5. add id to rows in csv

```
create-subject-csv \
 --input ../hse-data/mapping/v5/indicators_v5.csv \
 --output ../hse-data/mapping/v5/indicators_final_v5.csv \
 --namespace 'https://hse.ie/data/id/' \
 --id-template-column 'dct:identifier'
```

### 6. use rml-py to map csv to rdf

```
map2rdf --config ../hse-data/mapping/v5/config_v5.ttl
```

### 7. delete unnecessary triples

```
run-query \
	--ttl-file ../hse-data/mapping/v5/indicators_v5.ttl \
	--query-file sparql/general_transfer_v5.rq \
	--output ../hse-data/mapping/v5/indicators_final_v5.ttl
```

## Data Quality Report

### Completeness

### 1.2-1.4

```
dq-sparql \
	-e http://localhost:3030/v5/sparql \
	-s sparql/v2/completeness/1.2/ sparql/v2/completeness/1.3/ sparql/v2/completeness/1.4/ \
	-o ../hse-data/output/dq/v2/completeness_1.2-1.4.csv
```

### 1.5

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5/sparql \
	-s sparql/v2/completeness/1.5.rq \
	-o ../hse-data/output/dq/v2/completeness_1.5.csv
```

### 1.6

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5/sparql \
	-s sparql/v2/completeness/1.6.rq \
	-o ../hse-data/output/dq/v2/completeness_1.6.csv
```

### 1.7

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5/sparql \
	-s sparql/v2/completeness/1.7.rq \
	-o ../hse-data/output/dq/v2/completeness_1.7.csv
```

## Precision

### 2.1

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/precision/2.1.rq \
	-o ../hse-data/output/dq/v2/precision_2.1.csv
```

### 2.2

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/precision/2.2.rq \
	-o ../hse-data/output/dq/v2/precision_2.2.csv
```

## Timeline

### 3.1

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/timeline/3.1.rq \
	-o ../hse-data/output/dq/v2/timeline_3.1.csv
```

### 3.2

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/timeline/3.2.rq \
	-o ../hse-data/output/dq/v2/timeline_3.2.csv
```

## Data Protection

### 4.1

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/data_protection/4.1.rq \
	-o ../hse-data/output/dq/v2/data_protection_4.1.csv
```

### 4.2

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/data_protection/4.2.rq \
	-o ../hse-data/output/dq/v2/data_protection_4.2.csv
```

### 4.3

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/data_protection/4.3.rq \
	-o ../hse-data/output/dq/v2/data_protection_4.3.csv
```

## Indicators metdata fields present

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/indicators_metadata_fields_precent.rq  \
	-o ../hse-data/output/dq/v2/indicators_metadata_fields_precent.csv
```

## Datasets metadata field present

```
python -m scripts.pipeline_scripts.dq_sparql \
	-e http://localhost:3030/v5 \
	-s sparql/v2/datasets_metadata_fields_precent.rq  \
	-o ../hse-data/output/dq/v2/datasets_metadata_fields_precent.csv
```
