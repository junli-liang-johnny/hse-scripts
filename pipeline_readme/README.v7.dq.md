## Generate Fields Completeness Table
```
python -m scripts.pipeline.sparql.fields_completeness \
  -e http://localhost:3030/v5 \
  -o ../hse-data/output/dq/v7/mro_fields_completeness.csv
```

## Generate DQ Feasibility Test results
```
python -m scripts.pipeline.sparql.dq_feasibility_test \
  -e http://localhost:3030/v5 \
  -o ../hse-data/output/dq/v7/feasibility_test.csv
```