#!/usr/bin/env python3
"""
Data Quality Validator for HSE Pipeline

Validates datasets.csv and indicators.csv before pipeline execution.
Checks for:
  - Duplicate IDs and URLs
  - Missing critical fields
  - Placeholder/invalid rows
  - Frequency alignment between indicators and datasets
  - Publisher information completeness

Usage:
    hse-validate v10
    hse-validate v10 --strict
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Terminal colors
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _ok(msg: str) -> None:
    print(f"  {_GREEN}✓{_RESET} {msg}")


def _fail(msg: str) -> None:
    print(f"  {_RED}✗{_RESET} {msg}")


def _warn(msg: str) -> None:
    print(f"  {_YELLOW}⚠{_RESET} {msg}")


def _info(msg: str) -> None:
    print(f"  {_CYAN}ℹ{_RESET} {msg}")


def _header(msg: str) -> None:
    print()
    print("=" * 80)
    print(f"{_BOLD}{msg}{_RESET}")
    print("=" * 80)


def _section(msg: str) -> None:
    print()
    print(f"{_CYAN}──{_RESET} {_BOLD}{msg}{_RESET}")


# Frequency hierarchy for alignment checking
FREQUENCY_VALUES = {
    'WEEKLY': 52,
    'MONTHLY': 12,
    'QUARTERLY': 4,
    'ANNUAL': 1,
    'EVERY_2_YEARS': 0.5,
    'EVERY_3_YEARS': 0.33,
    'EVERY_5_YEARS': 0.2,
    'Every 6 years': 0.16,
    'AS_NEEDED': 0,
}


class ValidationResult:
    """Track validation results and errors"""
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks = 0
        self.failed_checks = 0
        self.warning_checks = 0

    def add_error(self, msg: str):
        self.errors.append(msg)
        self.failed_checks += 1
        _fail(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)
        self.warning_checks += 1
        _warn(msg)

    def add_pass(self, msg: str):
        self.passed_checks += 1
        _ok(msg)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> str:
        total = self.passed_checks + self.failed_checks + self.warning_checks
        return (f"Passed: {self.passed_checks}/{total} | "
                f"Failed: {self.failed_checks} | "
                f"Warnings: {self.warning_checks}")


def load_csv_with_metadata(file_path: Path, metadata_rows: int = 3) -> Tuple[List[Dict], List[str]]:
    """
    Load CSV file with multi-row metadata headers.
    
    Args:
        file_path: Path to CSV file
        metadata_rows: Number of metadata rows before data (default 3 for indicators, 4 for datasets)
    
    Returns:
        Tuple of (data rows as list of dicts, field names)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # First line contains field names
    field_names = [h.strip() for h in lines[0].strip().split(',')]
    
    # Skip metadata rows and parse data
    reader = csv.DictReader(lines[metadata_rows:], fieldnames=field_names)
    data = list(reader)
    
    return data, field_names


def validate_datasets(datasets_path: Path, result: ValidationResult) -> Dict[str, Dict]:
    """Validate datasets.csv"""
    _section("Validating datasets.csv")
    
    if not datasets_path.exists():
        result.add_error(f"datasets.csv not found: {datasets_path}")
        return {}
    
    try:
        datasets, _ = load_csv_with_metadata(datasets_path, metadata_rows=4)
    except Exception as e:
        result.add_error(f"Failed to load datasets.csv: {e}")
        return {}
    
    if not datasets:
        result.add_error("datasets.csv is empty")
        return {}
    
    result.add_pass(f"Loaded {len(datasets)} dataset rows")
    
    # Build dataset lookup by URL
    dataset_lookup = {}
    
    # Check for duplicate URLs
    urls = [d.get('URL (identifier)', '').strip() for d in datasets]
    url_counts = Counter(urls)
    duplicates = {url: count for url, count in url_counts.items() if count > 1 and url}
    
    if duplicates:
        result.add_error(f"Found {len(duplicates)} duplicate dataset URLs:")
        for url, count in sorted(duplicates.items())[:5]:  # Show first 5
            print(f"      {url} (appears {count} times)")
        if len(duplicates) > 5:
            print(f"      ... and {len(duplicates) - 5} more")
    else:
        result.add_pass("No duplicate dataset URLs")
    
    # Check for missing critical fields
    missing_url = [d for d in datasets if not d.get('URL (identifier)', '').strip()]
    missing_name = [d for d in datasets if not d.get('Dataset Name', '').strip()]
    missing_publisher = [d for d in datasets if not d.get('Publisher Name', '').strip()]
    
    if missing_url:
        result.add_error(f"{len(missing_url)} datasets missing URL (identifier)")
    else:
        result.add_pass("All datasets have URLs")
    
    if missing_name:
        result.add_error(f"{len(missing_name)} datasets missing Dataset Name")
    else:
        result.add_pass("All datasets have names")
    
    if missing_publisher:
        result.add_error(f"{len(missing_publisher)} datasets missing Publisher Name")
        for d in missing_publisher[:3]:  # Show first 3
            print(f"      {d.get('URL (identifier)', 'Unknown URL')}")
    else:
        result.add_pass("All datasets have publishers")
    
    # Check for placeholder rows (no URL)
    valid_datasets = [d for d in datasets if d.get('URL (identifier)', '').strip()]
    if len(valid_datasets) < len(datasets):
        diff = len(datasets) - len(valid_datasets)
        result.add_warning(f"{diff} placeholder/invalid rows without URLs")
    
    # Build lookup dictionary
    for d in valid_datasets:
        url = d.get('URL (identifier)', '').strip()
        if url:
            dataset_lookup[url] = d
    
    # Publisher statistics
    publishers = set(d.get('Publisher Name', '') for d in valid_datasets 
                    if d.get('Publisher Name', ''))
    _info(f"Found {len(publishers)} unique publishers: {', '.join(sorted(publishers)[:5])}...")
    
    return dataset_lookup


def validate_indicators(indicators_path: Path, result: ValidationResult) -> List[Dict]:
    """Validate indicators.csv"""
    _section("Validating indicators.csv")
    
    if not indicators_path.exists():
        result.add_error(f"indicators.csv not found: {indicators_path}")
        return []
    
    try:
        indicators, _ = load_csv_with_metadata(indicators_path, metadata_rows=3)
    except Exception as e:
        result.add_error(f"Failed to load indicators.csv: {e}")
        return []
    
    if not indicators:
        result.add_error("indicators.csv is empty")
        return []
    
    result.add_pass(f"Loaded {len(indicators)} indicator rows")
    
    # Check for duplicate IDs
    ids = [i.get('Indicator ID', '').strip() for i in indicators]
    id_counts = Counter(ids)
    duplicates = {id: count for id, count in id_counts.items() if count > 1 and id}
    
    if duplicates:
        result.add_error(f"Found {len(duplicates)} duplicate indicator IDs:")
        for id, count in sorted(duplicates.items())[:5]:  # Show first 5
            print(f"      {id} (appears {count} times)")
    else:
        result.add_pass("No duplicate indicator IDs")
    
    # Check for missing critical fields
    missing_id = [i for i in indicators if not i.get('Indicator ID', '').strip()]
    missing_title = [i for i in indicators if not i.get('Indicator Title', '').strip()]
    missing_def = [i for i in indicators if not i.get('Definition', '').strip()]
    
    if missing_id:
        result.add_error(f"{len(missing_id)} indicators missing Indicator ID")
    else:
        result.add_pass("All indicators have IDs")
    
    if missing_title:
        result.add_error(f"{len(missing_title)} indicators missing Indicator Title")
    else:
        result.add_pass("All indicators have titles")
    
    if missing_def:
        result.add_error(f"{len(missing_def)} indicators missing Definition")
    else:
        result.add_pass("All indicators have definitions")
    
    # Check Domain field (informational only)
    missing_domain = [i for i in indicators if not i.get('Domain', '').strip()]
    if missing_domain and len(missing_domain) == len(indicators):
        _info("Domain field is empty for all indicators (Subdomain is populated)")
    elif missing_domain:
        result.add_warning(f"{len(missing_domain)} indicators missing Domain")
    
    return indicators


def validate_frequency_alignment(indicators: List[Dict], dataset_lookup: Dict[str, Dict], 
                                 result: ValidationResult, strict: bool = False):
    """Validate frequency alignment between indicators and datasets"""
    _section("Validating frequency alignment")
    
    if not indicators or not dataset_lookup:
        result.add_warning("Skipping frequency validation (missing data)")
        return
    
    mismatches = []
    census_patterns = 0
    checked_pairs = 0
    
    for indicator in indicators:
        ind_id = indicator.get('Indicator ID', '').strip()
        ind_freq_str = indicator.get('Report Frequency', '').strip()
        
        if not ind_id or not ind_freq_str:
            continue
        
        # Check numerator and denominator datasets
        for dataset_field in ['Numerator Source Dataset', 'Denominator Source Dataset']:
            dataset_url = indicator.get(dataset_field, '').strip()
            
            if not dataset_url or dataset_url not in dataset_lookup:
                continue
            
            dataset = dataset_lookup[dataset_url]
            dataset_freq_str = dataset.get('Frequency of data updates', '').strip()
            
            if not dataset_freq_str:
                continue
            
            checked_pairs += 1
            
            # Get frequency values
            ind_freq = FREQUENCY_VALUES.get(ind_freq_str, -1)
            dataset_freq = FREQUENCY_VALUES.get(dataset_freq_str, -1)
            
            if ind_freq == -1 or dataset_freq == -1:
                continue
            
            # Check if indicator frequency is lower than dataset frequency
            # (indicator should not update more frequently than its data source)
            if ind_freq > dataset_freq:
                # Check if this is a census denominator pattern (acceptable)
                dataset_name_lower = dataset.get('Dataset Name', '').lower()
                if ('census' in dataset_url.lower() or 
                    'census' in dataset_name_lower or 
                    'C2016' in dataset_url or
                    'C2022' in dataset_url):
                    census_patterns += 1
                else:
                    mismatches.append({
                        'indicator_id': ind_id,
                        'indicator_freq': ind_freq_str,
                        'dataset_url': dataset_url,
                        'dataset_name': dataset.get('Dataset Name', 'Unknown'),
                        'dataset_freq': dataset_freq_str,
                        'field': dataset_field
                    })
    
    _info(f"Checked {checked_pairs} indicator-dataset pairs")
    
    if census_patterns > 0:
        _info(f"Found {census_patterns} acceptable census denominator patterns")
    
    if mismatches:
        result.add_error(f"Found {len(mismatches)} frequency mismatches:")
        for m in mismatches[:5]:  # Show first 5
            print(f"      {m['indicator_id']}: {m['indicator_freq']} vs "
                  f"{m['dataset_name']}: {m['dataset_freq']}")
        if len(mismatches) > 5:
            print(f"      ... and {len(mismatches) - 5} more")
    else:
        result.add_pass("No frequency mismatches (excluding census denominators)")


def validate_version(version: str, strict: bool = False) -> int:
    """
    Validate a specific version's data quality.
    
    Args:
        version: Pipeline version (e.g., 'v10')
        strict: If True, warnings are treated as errors
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    _header(f"Data Quality Validation: {version.upper()}")
    
    # Determine paths
    scripts_root = Path(__file__).parent.parent.parent
    data_root = scripts_root.parent / "hse-data"
    mapping_dir = data_root / "mapping" / version
    
    datasets_path = mapping_dir / "datasets.csv"
    indicators_path = mapping_dir / "indicators.csv"
    
    print(f"\nValidation directory: {mapping_dir}")
    
    result = ValidationResult()
    
    # Run validations
    dataset_lookup = validate_datasets(datasets_path, result)
    indicators = validate_indicators(indicators_path, result)
    
    if dataset_lookup and indicators:
        validate_frequency_alignment(indicators, dataset_lookup, result, strict)
    
    # Print summary
    _header("Validation Summary")
    print(f"\n{result.summary()}")
    
    if result.has_errors():
        print(f"\n{_RED}✗ VALIDATION FAILED{_RESET}")
        print(f"  {len(result.errors)} error(s) must be fixed before running pipeline")
        return 1
    elif result.warnings and strict:
        print(f"\n{_YELLOW}⚠ VALIDATION FAILED (strict mode){_RESET}")
        print(f"  {len(result.warnings)} warning(s) treated as errors in strict mode")
        return 1
    else:
        print(f"\n{_GREEN}✓ VALIDATION PASSED{_RESET}")
        if result.warnings:
            print(f"  {len(result.warnings)} warning(s) - review recommended but not blocking")
        print(f"\n{_GREEN}🚀 Ready for pipeline execution!{_RESET}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate HSE pipeline input data quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hse-validate v10              Validate v10 pipeline inputs
  hse-validate v10 --strict     Treat warnings as errors
        """,
    )
    parser.add_argument("version", help="Pipeline version (e.g., v10, v9)")
    parser.add_argument("--strict", action="store_true",
                       help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    exit_code = validate_version(args.version, args.strict)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
