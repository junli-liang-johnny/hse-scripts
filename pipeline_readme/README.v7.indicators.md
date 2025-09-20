# v7 master data catalogue uplifting
## Indicators
## 1. convert original csv to rdf-ready csv (data cleaning)

```
csv-rdf-convert \
	--input "../hse-data/data/schema/OAHP_MasterDataCatalogueVersion0007.xlsx - Indicators.csv" \
	--row-index-remove 0 2 \
	--output ../hse-data/mapping/v7/indicators.csv
```

## 2. create indicators dcat datasets

```
create-csv \
	--input ../hse-data/mapping/v7/indicators.csv \
	--output ../hse-data/mapping/v7/indicators_dcat-dataset.csv \
	--column 'phi:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
	--header 'id' 'rdf:type' 'dcterms:publisher' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index -1 \
	--optional-values-to-insert 'dcat:Dataset' 'https://hse.ie/data/id/{uuid}'
```

## 3. create indicators publishers

```
create-csv \
	--input ../hse-data/mapping/v7/indicators.csv \
	--output ../hse-data/mapping/v7/indicators_publishers.csv \
	--column 'phi:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
	--header 'id' 'rdf:type' 'dcterms:source' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index 2 \
	--optional-values-to-insert 'dct:Publisher' \
	--identifier-csv ../hse-data/mapping/indicators_dcat-dataset.csv \
	--identifier-column dcterms:publisher
```

## 4. create indicators provenance

```
create-csv \
	--input ../hse-data/mapping/v7/indicators.csv \
	--output ../hse-data/mapping/v7/indicators_provenance.csv \
	--column 'dct:provenance [a dct:ProvenanceStatement; rdfs:label ]' \
	--header 'id' 'rdf:type' 'rdfs:label' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index 2 \
	--optional-values-to-insert 'dcterms:ProvenanceStatement'
```

## 5. add id to rows in csv

```
create-subject-csv \
 --input ../hse-data/mapping/v7/indicators.csv \
 --output ../hse-data/mapping/v7/indicators_final.csv \
 --namespace 'https://hse.ie/data/id/' \
 --id-template-column 'dct:identifier'
```

## 6. use rml-py to map csv to rdf

```
map2rdf --config ../hse-data/mapping/v7/config.ttl
```

## 7. delete unnecessary triples

```
run-query \
	--ttl-file ../hse-data/mapping/v7/indicators.ttl \
	--query-file sparql/general_transfer_v7.rq \
	--output ../hse-data/mapping/v7/indicators_final.ttl
```