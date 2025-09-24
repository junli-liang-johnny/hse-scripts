echo "Converting OAHP Master Data Catalogue Version 0007 - Indicators.csv to RDF..."
csv-rdf-convert \
	--input "../hse-data/data/schema/OAHP_MasterDataCatalogueVersion0007.xlsx - Indicators.csv" \
	--row-index-remove 0 2 \
	--output ../hse-data/mapping/v8/indicators.csv

echo "Creating DCAT Dataset from Indicators.csv..."
create-csv \
	--input ../hse-data/mapping/v8/indicators.csv \
	--output ../hse-data/mapping/v8/indicators_dcat-dataset.csv \
	--column 'phi:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
	--header 'id' 'rdf:type' 'dcterms:publisher' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index -1 \
	--optional-values-to-insert 'dcat:Dataset' 'https://hse.ie/data/id/{uuid}'

echo "Creating DCAT Publisher from Indicators.csv..."
create-csv \
	--input ../hse-data/mapping/v8/indicators.csv \
	--output ../hse-data/mapping/v8/indicators_publishers.csv \
	--column 'phi:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
	--header 'id' 'rdf:type' 'dcterms:source' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index 2 \
	--optional-values-to-insert 'dct:Publisher' \
	--identifier-csv ../hse-data/mapping/indicators_dcat-dataset.csv \
	--identifier-column dcterms:publisher

echo "Creating DCAT ProvenanceStatement from Indicators.csv..."
create-csv \
	--input ../hse-data/mapping/v8/indicators.csv \
	--output ../hse-data/mapping/v8/indicators_provenance.csv \
	--column 'dct:provenance [a dct:ProvenanceStatement; rdfs:label ]' \
	--header 'id' 'rdf:type' 'rdfs:label' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index 2 \
	--optional-values-to-insert 'dcterms:ProvenanceStatement'

echo "Creating identifiers for Indicators.csv..."
create-subject-csv \
 --input ../hse-data/mapping/v8/indicators.csv \
 --output ../hse-data/mapping/v8/indicators_final.csv \
 --namespace 'https://hse.ie/data/id/' \
 --id-template-column 'dct:identifier'

echo "Converting OAHP Master Data Catalogue Version 0007 - Datasets.csv to RDF..."
csv-rdf-convert \
  --input "../hse-data/data/schema/OAHP_MasterDataCatalogueVersion0008.xlsx - Datasets.csv" \
  --row-index-remove 0 2 3 \
  --output ../hse-data/mapping/v8/datasets.csv

echo "Creating DCAT Dataset from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_publishers.csv \
 --column 'dct:publisher [ a dct:Publisher; foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:Publisher' \
 --identifier-csv ../hse-data/mapping/v8/datasets.csv \
 --identifier-column 'dct:publisher'

echo "Creating DCAT ProvenanceStatement from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_provenance.csv \
 --column 'dct:Provenance [a dct:ProvenanceStatement; rdfs:label ]' \
 --header 'id' 'rdf:type' 'rdfs:label' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcterms:ProvenanceStatement'

echo "Creating DCAT ContactPoint from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_contact_point.csv \
 --column 'dcat:contactPoint [vcard:individual vcard:fn]' \
 --header 'id' 'rdf:type' 'vcard:fn' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'vcard:Individual'

echo "Creating DCAT Data Coverage Start Date from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_data_coverage_start_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:startDate ""^^xsd:dateTime; dcat:endDate ""^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:startDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'

echo "Creating DCAT Data Coverage End Date from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_data_coverage_end_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:endDate ""^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:endDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'

echo "Creating DCAT Distributions from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_distributions.csv \
 --column 'dcat:distribution [ a dcat:Distribution; dct:format]' \
 --header 'id' 'rdf:type' 'dct:format' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'

echo "Creating ADMS Sample from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_adms_sample.csv \
 --column 'adms:sample[ a dcat:Distribution; dcat:accessURL]' \
 --header 'id' 'rdf:type' 'dcat:accessURL' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'

echo "Creating Health DCAT AP HDAB from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_healthdcatap:hdab.csv \
 --column 'healthdcatap:hdab [a foaf:Agent; foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'foaf:Agent'

echo "Creating identifiers for Datasets.csv..."
create-subject-csv \
 --input ../hse-data/mapping/v8/datasets.csv \
 --output ../hse-data/mapping/v8/datasets_final.csv \
 --namespace '' \
 --id-template-column 'dct:identifier'

echo "Generating RDF from CSV files using RML mapping..."
map2rdf --config ../hse-data/mapping/v8/config.ttl

echo "Merging all generated TTL files into a single datasets.ttl file..."
run-query \
	--ttl-file ../hse-data/mapping/v8/datasets.ttl \
	--query-file sparql/general_transfer.rq \
	--output ../hse-data/mapping/v8/datasets_final.ttl

echo "Running final transformations on datasets_final.ttl..."
run-query \
	--ttl-file ../hse-data/mapping/v8/datasets.ttl \
	--query-file ./sparql/datasets_transfer_v5.rq \
	--output ../hse-data/mapping/v8/datasets_final.ttl

echo "Running final transformations on indicators_final.ttl..."
run-query \
	--ttl-file ../hse-data/mapping/v8/indicators.ttl \
	--query-file sparql/general_transfer_v7.rq \
	--output ../hse-data/mapping/v8/indicators_final.ttl

echo "All done!"

echo "Generating MRO fields completeness report..."
python -m scripts.pipeline_scripts.sparql.fields_completeness \
  -e http://localhost:3030/v5 \
  -o ../hse-data/output/dq/v8/mro_fields_completeness.csv

echo "Generating DQ Feasibility Test report..."
python -m scripts.pipeline_scripts.sparql.dq_feasibility_test \
  -e http://localhost:3030/v5 \
  -o ../hse-data/output/dq/v8/feasibility_test.csv