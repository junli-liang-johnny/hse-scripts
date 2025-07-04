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
python -m scripts.rdf_mapping.csv_rdf_convert \
 --input ./data/cso/combined_datasets.csv \
 --output ./mapping/datasets.csv
```

### 2. create datasets' publisher

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_publishers.csv \
 --column 'dct:publisher' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/publisher/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:Publisher' \
 --identifier-csv ./mapping/datasets.csv \
 --identifier-column dct:publisher
```

### 4. create datasets provenance

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_provenance.csv \
 --column 'dct:Provenance' \
 --header 'id' 'rdf:type' 'rdfs:label' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/provenance/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcterms:ProvenanceStatement'
```

### 5. create datasets contact point

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_contact_point.csv \
 --column 'dcat:contactPoint' \
 --header 'id' 'rdf:type' 'vcard:fn' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/contact-point/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'vcard:Individual'
```

### 6. create datasets Data Coverage Start Date

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_data_coverage_start_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:startDate "^^xsd:dateTime; dcat:endDate "^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:startDate' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/data-coverage-date/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'
```

### 7. create datasets Data Coverage End Date

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_data_coverage_end_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:endDate "^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:endDate' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/data-coverage-date/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'
```

### 8. create datasets distributions

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_distributions.csv \
 --column 'dcat:distribution' \
 --header 'id' 'rdf:type' 'dct:format' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/distribution/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'
```

### 9. create datasets adms:sample

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_adms_sample.csv \
 --column 'adms:sample' \
 --header 'id' 'rdf:type' 'dcat:accessURL' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/adms-sample/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'
```

### 10. create datasets healthdcatap:hdab

```
python -m scripts.rdf_mapping.create_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_healthdcatap:hdab.csv \
 --column 'healthdcatap:hdab [a foaf:Agent; foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie' \
 --id-template '/hdab/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'foaf:Agent'
```

### 5. add id to rows in csv

```
python -m scripts.rdf_mapping.create_subject_csv \
 --input ./mapping/datasets.csv \
 --output ./mapping/datasets_final.csv \
 --namespace 'https://hse-oahwb-profile.adaptcentre.ie/dataset/' \
 --id-template-column 'dct:identifier' \
 --split-by "/" \
 --template-split-index -1
```

### 6. use rml-py to map csv to rdf

```
python -m scripts.rdf_mapping.map_to_rdf --config ./mapping/config.ttl
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
