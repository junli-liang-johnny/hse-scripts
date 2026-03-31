# HSE Data Quality Validator

## Overview

The `hse-validate` command checks your pipeline input data for quality issues before running the pipeline. It validates both `datasets.csv` and `indicators.csv`.

## Usage

```bash
# Basic validation
hse-validate v10

# Strict mode (treats warnings as errors)
hse-validate v10 --strict

# Check other versions
hse-validate v9
```

## What It Checks

### Datasets (datasets.csv)

- ✓ No duplicate dataset URLs
- ✓ All datasets have valid URLs (identifier)
- ✓ All datasets have names
- ✓ All datasets have publisher information
- ✓ No placeholder/invalid rows

### Indicators (indicators.csv)

- ✓ No duplicate indicator IDs
- ✓ All indicators have unique IDs
- ✓ All indicators have titles
- ✓ All indicators have definitions
- ℹ Domain field population (informational)

### Frequency Alignment

- ✓ Indicator report frequencies align with dataset update frequencies
- ℹ Census denominator patterns are acceptable (e.g., ANNUAL indicator with EVERY_5_YEARS census data)
- ✗ Non-census mismatches are flagged (indicator can't update more frequently than its data source)

## Validation Results

### Exit Codes

- `0` - All checks passed, pipeline ready to run
- `1` - Validation failed, issues must be fixed

### Output Levels

- ✓ **Pass** - Check passed successfully
- ✗ **Error** - Critical issue that blocks pipeline execution
- ⚠ **Warning** - Issue that should be reviewed but doesn't block pipeline
- ℹ **Info** - Informational message

## Integration with Pipeline

Recommended workflow:

```bash
# 1. Validate data quality
hse-validate v10

# 2. If validation passes, run pipeline
hse-pipeline run v10
```

Or combine them:

```bash
hse-validate v10 && hse-pipeline run v10
```

## Common Issues and Fixes

### Duplicate Dataset URLs

**Issue**: Same dataset URL appears multiple times  
**Fix**: Use deduplication script or manually remove duplicates keeping first occurrence

### Missing Publishers

**Issue**: Datasets without Publisher Name  
**Fix**: Infer from URL patterns or add manually

### Frequency Mismatches

**Issue**: Indicator updates more frequently than data source  
**Fix**: Align indicator frequency with dataset frequency, OR update dataset frequency if incorrect

**Acceptable patterns**:

- Census denominators (annual indicators using census data)
- Static reference data supporting any frequency

**Not acceptable**:

- WEEKLY indicator using ANNUAL dataset
- MONTHLY indicator using QUARTERLY dataset

### Placeholder Rows

**Issue**: Rows without valid URL identifiers  
**Fix**: Remove non-dataset rows from datasets.csv

## Example Output

```
================================================================================
Data Quality Validation: V10
================================================================================

Validation directory: /home/johnny/workspace/hse/hse-data/mapping/v10

── Validating datasets.csv
  ✓ Loaded 228 dataset rows
  ✓ No duplicate dataset URLs
  ✓ All datasets have publishers
  ℹ Found 16 unique publishers

── Validating indicators.csv
  ✓ Loaded 275 indicator rows
  ✓ No duplicate indicator IDs
  ✓ All indicators have definitions

── Validating frequency alignment
  ℹ Checked 366 indicator-dataset pairs
  ℹ Found 34 acceptable census denominator patterns
  ✓ No frequency mismatches

================================================================================
Validation Summary
================================================================================

Passed: 11/11 | Failed: 0 | Warnings: 0

✓ VALIDATION PASSED
🚀 Ready for pipeline execution!
```

## Advanced Options

### Strict Mode

Use `--strict` to treat warnings as errors:

```bash
hse-validate v10 --strict
```

This is useful for:

- CI/CD pipelines requiring no warnings
- High-quality production releases
- Enforcing data governance policies

## Troubleshooting

### Command not found

If `hse-validate` is not recognized:

```bash
# Reinstall the package
cd /path/to/hse-scripts
pip install -e .
```

### ImportError or module issues

Check that you're using the correct Python environment:

```bash
# Activate the virtual environment
source /path/to/hse-scripts/.env/bin/activate

# Verify installation
which hse-validate
```

### False positives

If the validator flags issues you believe are correct:

1. Review the specific error message
2. Check the frequency hierarchy (WEEKLY > MONTHLY > QUARTERLY > ANNUAL > EVERY_2_YEARS, etc.)
3. Verify census patterns are properly detected
4. Contact the data pipeline team if you believe it's a validator bug

## File Format Requirements

### CSV Structure

Both files use multi-row metadata headers:

- **datasets.csv**: 4 metadata rows (RDF predicates, M/R/O indicators, etc.)
- **indicators.csv**: 3 metadata rows

The validator automatically handles these metadata rows.

### Required Fields

**datasets.csv**:

- URL (identifier) - Unique dataset identifier
- Dataset Name
- Publisher Name
- Frequency of data updates

**indicators.csv**:

- Indicator ID - Unique identifier (hseNNNNNNN format)
- Indicator Title
- Definition
- Report Frequency
- Numerator Source Dataset (URL)
- Denominator Source Dataset (URL, if applicable)

## Version History

- **v1.0** (2026-03-30): Initial release
  - Dataset validation
  - Indicator validation
  - Frequency alignment checking
  - Census pattern detection
