echo "Creating DCAT Dataset from Indicators.csv..."
create-csv \
	--input ../hse-data/mapping/v10/indicators.csv \
	--output ../hse-data/mapping/v10/indicators_dcat-dataset.csv \
	--column 'phi:numeratorSource [a dct:dataset [a dct:publisher [a dcterms:source]]' \
	--header 'id' 'rdf:type' 'dcterms:publisher' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index -1 \
	--optional-values-to-insert 'dcat:Dataset' 'https://hse.ie/data/id/{uuid}'

echo "Creating DCAT Publisher from Indicators.csv..."
create-csv \
	--input ../hse-data/mapping/v10/indicators.csv \
	--output ../hse-data/mapping/v10/indicators_publishers.csv \
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
	--input ../hse-data/mapping/v10/indicators.csv \
	--output ../hse-data/mapping/v10/indicators_provenance.csv \
	--column 'dct:provenance [a dct:ProvenanceStatement; rdfs:label ]' \
	--header 'id' 'rdf:type' 'rdfs:label' \
	--namespace 'https://hse.ie' \
	--id-template '/data/id/{uuid}' \
	--extracted-value-insert-index 2 \
	--optional-values-to-insert 'dcterms:ProvenanceStatement'

echo "Creating identifiers for Indicators.csv..."
create-subject-csv \
 --input ../hse-data/mapping/v10/indicators.csv \
 --output ../hse-data/mapping/v10/indicators_final.csv \
 --namespace 'https://hse.ie/data/id/' \
 --id-template-column 'dct:identifier'

# echo "Converting OAHP Master Data Catalogue Version 0010 - Datasets.csv to RDF..."
# csv-rdf-convert \
#   --input "../hse-data/data/schema/OAHP_MasterDataCatalogueVersion0010.xlsx - Datasets.csv" \
#   --row-index-remove 0 2 3 \
#   --output ../hse-data/mapping/v10/datasets.csv

echo "Creating DCAT Dataset from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_publishers.csv \
 --column 'dct:publisher [ a dct:Publisher; foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:Publisher' \
 --identifier-csv ../hse-data/mapping/v10/datasets.csv \
 --identifier-column 'dct:publisher'

echo "Creating DCAT ProvenanceStatement from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_provenance.csv \
 --column 'dct:Provenance [a dct:ProvenanceStatement; rdfs:label ]' \
 --header 'id' 'rdf:type' 'rdfs:label' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcterms:ProvenanceStatement'

echo "Creating DCAT ContactPoint from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_contact_point.csv \
 --column 'dcat:contactPoint [vcard:individual vcard:fn]' \
 --header 'id' 'rdf:type' 'vcard:fn' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'vcard:Individual'

echo "Creating DCAT Data Coverage Start Date from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_data_coverage_start_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:startDate ""^^xsd:dateTime; dcat:endDate ""^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:startDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'

echo "Creating DCAT Data Coverage End Date from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_data_coverage_end_date.csv \
 --column 'dcterms:temporal [a dct:PeriodOfTime; dcat:endDate ""^^xsd:dateTime.]' \
 --header 'id' 'rdf:type' 'dcat:endDate' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dct:PeriodOfTime'

echo "Creating DCAT Distributions from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_distributions.csv \
 --column 'dcat:distribution [ a dcat:Distribution; dct:format]' \
 --header 'id' 'rdf:type' 'dct:format' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'

echo "Creating ADMS Sample from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_adms_sample.csv \
 --column 'adms:sample[ a dcat:Distribution; dcat:accessURL]' \
 --header 'id' 'rdf:type' 'dcat:accessURL' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcat:Distribution'

echo "Creating Health DCAT AP HDAB from Datasets.csv..."
create-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_healthdcatap:hdab.csv \
 --column 'healthdcatap:hdab [a foaf:Agent; foaf:name ]' \
 --header 'id' 'rdf:type' 'foaf:name' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'foaf:Agent'

echo "Creating identifiers for Datasets.csv..."
create-subject-csv \
 --input ../hse-data/mapping/v10/datasets.csv \
 --output ../hse-data/mapping/v10/datasets_final.csv \
 --namespace '' \
 --id-template-column 'dct:identifier'

# Indicator groups
echo "Creating Provenance Statements from Indicator Groups.csv..."
create-csv \
 --input ../hse-data/mapping/v10/indicator_groups.csv \
 --output ../hse-data/mapping/v10/indicator_groups_provenance.csv \
 --column 'dct:provenance [a dct:ProvenanceStatement; rdfs:label ]' \
 --header 'id' 'rdf:type' 'rdfs:label' \
 --namespace 'https://hse.ie' \
 --id-template '/data/id/{uuid}' \
 --extracted-value-insert-index 2 \
 --optional-values-to-insert 'dcterms:ProvenanceStatement'

echo "Generating RDF from CSV files using RML mapping..."
rmlmapper -o ../hse-data/mapping/v10/mappings.ttl -m ../hse-data/mapping/v10/config.ttl -s turtle

echo "Running SPARQL transformations (part 1: entity linking)..."
run-query \
	--ttl-file ../hse-data/mapping/v10/mappings.ttl \
	--query-file sparql/v10_transformations_part1.rq \
	--output ../hse-data/mapping/v10/mappings_temp1.ttl

echo "Running SPARQL transformations (part 2a: Indicator accrualPeriodicity)..."
run-query \
	--ttl-file ../hse-data/mapping/v10/mappings_temp1.ttl \
	--query-file sparql/v10_transformations_part2a.rq \
	--output ../hse-data/mapping/v10/mappings_temp2.ttl

echo "Running SPARQL transformations (part 2b: Dataset accrualPeriodicity)..."
run-query \
	--ttl-file ../hse-data/mapping/v10/mappings_temp2.ttl \
	--query-file sparql/v10_transformations_part2b.rq \
	--output ../hse-data/mapping/v10/mappings_final.ttl

echo "Cleaning up temporary files..."
rm -f ../hse-data/mapping/v10/mappings_temp1.ttl ../hse-data/mapping/v10/mappings_temp2.ttl

echo ""
echo "Counting triples in generated RDF files..."
python -m scripts.count_triples

echo ""
echo "=========================================="
echo "Pipeline complete!"
echo "=========================================="

echo "Generating MRO fields completeness report..."
mkdir -p ../hse-data/output/dq/v10
python -m scripts.pipeline_scripts.sparql.fields_completeness_rdflib \
  -r ../hse-data/mapping/v10/mappings_final.ttl ../hse-data/mapping/phpt.ttl \
  -q sparql/v2/MRO_completeness.rq \
  -o ../hse-data/output/dq/v10/mro_fields_completeness.csv

echo "Generating DQ Feasibility Test report..."
python -m scripts.pipeline_scripts.sparql.dq_feasibility_test_rdflib \
  -r ../hse-data/mapping/v10/mappings_final.ttl ../hse-data/mapping/phpt.ttl \
  -q sparql/v2/feasibility_check.rq \
  -o ../hse-data/output/dq/v10/feasibility_test.csv