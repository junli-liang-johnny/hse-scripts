# Pipeline steps for datasets

## 1. convert original csv to rdf-ready csv (data cleaning)

```
csv-rdf-convert \
  --input "../hse-data/data/schema/OAHP_MasterDataCatalogueVersion0007.xlsx - Datasets.csv" \
  --row-index-remove 0 2 3 \
  --output ../hse-data/mapping/v7/datasets.csv
```

## 2. create datasets' publisher

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
 --identifier-column 'dct:publisher'
```

## 4. create datasets provenance

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

## 5. create datasets contact point

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_contact_point.csv \
 --column 'dcat:contactPoint [vcard:individual vcard:fn]' \
 --header 'id' 'rdf:type' 'vcard:fn' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'vcard:Individual'
```

## 6. create datasets Data Coverage Start Date

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_data_coverage_start_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:startDate ""^^xsd:dateTime; dcat:endDate ""^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:startDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'
```

## 7. create datasets Data Coverage End Date

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_data_coverage_end_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:endDate ""^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:endDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'
```

## 8. create datasets distributions

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

## 9. create datasets adms:sample

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

## 10. create datasets healthdcatap:hdab

```
create-csv \
 --input ../hse-data/mapping/v7/datasets.csv \
 --output ../hse-data/mapping/v7/datasets_healthdcatap:hdab.csv \
 --column 'healthdcatap:hdab [a foaf:Agent; foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'foaf:Agent'
```

## 11. add id to rows in csv

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
 --namespace '' \
 --id-template-column 'dct:identifier'
```

## 12. use rml-py to map csv to rdf

```
map2rdf --config ../hse-data/mapping/v7/config.ttl
```

## 13. delete unnecessary triples

```
run-query \
	--ttl-file ../hse-data/mapping/v7/datasets.ttl \
	--query-file sparql/general_transfer.rq \
	--output ../hse-data/mapping/v7/datasets_final.ttl
```

## 14. data transformation

"dpv:NonPersonalData" -> dpv:NonPersonalData

```
run-query \
	--ttl-file ../hse-data/mapping/v7/datasets.ttl \
	--query-file ./sparql/datasets_transfer_v5.rq \
	--output ../hse-data/mapping/v7/datasets_final.ttl
```