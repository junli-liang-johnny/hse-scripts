#!/usr/bin/env python3
"""
Generate a completeness summary table from mro_fields_completeness_raw.csv
"""

import argparse
import csv
import sys
from pathlib import Path

def calculate_completeness_summary(input_file):
    """Calculate mean completeness for different field categories"""
    
    required_values = []
    mandatory_values = []
    recommended_values = []
    optional_values = []
    overall_values = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert percentage strings to floats
            if row['requiredFieldCompletenessPercent']:
                required_values.append(float(row['requiredFieldCompletenessPercent']))
            if row['mandatoryCompletenessPercent']:
                mandatory_values.append(float(row['mandatoryCompletenessPercent']))
            if row['recommendedCompletenessPercent']:
                recommended_values.append(float(row['recommendedCompletenessPercent']))
            if row['optionalCompletenessPercent']:
                optional_values.append(float(row['optionalCompletenessPercent']))
            if row['overallCompletenessPercent']:
                overall_values.append(float(row['overallCompletenessPercent']))
    
    n = len(overall_values)
    
    # Calculate means
    required_mean = sum(required_values) / len(required_values) * 100 if required_values else 0
    mandatory_mean = sum(mandatory_values) / len(mandatory_values) * 100 if mandatory_values else 0
    recommended_mean = sum(recommended_values) / len(recommended_values) * 100 if recommended_values else 0
    optional_mean = sum(optional_values) / len(optional_values) * 100 if optional_values else 0
    overall_mean = sum(overall_values) / len(overall_values) * 100 if overall_values else 0
    
    # Print table
    print("\nIndicators Field Completeness Summary")
    print("=" * 60)
    print(f"{'Entity Type':<50} | {'Mean Completeness':>15}")
    print("-" * 60)
    print(f"{'Indicators Overall (n=' + str(n) + ')':<50} | {overall_mean:>14.2f}%")
    print(f"{'Indicators Mandatory Fields (n=' + str(n) + ')':<50} | {mandatory_mean:>14.2f}%")
    print(f"{'Indicators Recommended Fields (n=' + str(n) + ')':<50} | {recommended_mean:>14.2f}%")
    print(f"{'Indicators Optional Fields (n=' + str(n) + ')':<50} | {optional_mean:>14.2f}%")
    print(f"{'Fields Required to Generate Report (n=' + str(n) + ')':<50} | {required_mean:>14.2f}%")
    print("=" * 60)
    print()
    
    return {
        'n': n,
        'overall_mean': overall_mean,
        'mandatory_mean': mandatory_mean,
        'recommended_mean': recommended_mean,
        'optional_mean': optional_mean,
        'required_mean': required_mean
    }

def main():
    """CLI entry point"""
    # Default to v10 output in hse-data directory
    # Assuming hse-scripts and hse-data are sibling directories
    script_dir = Path(__file__).parent
    default_file = script_dir.parent.parent.parent / "hse-data" / "output" / "dq" / "v10" / "mro_fields_completeness_raw.csv"
    
    parser = argparse.ArgumentParser(
        description='Generate completeness summary table from mro_fields_completeness_raw.csv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use default file (v10)
  hse-completeness
  
  # Specify custom file
  hse-completeness /path/to/mro_fields_completeness_raw.csv
  
  # Use v9 data
  hse-completeness ../hse-data/output/dq/v9/mro_fields_completeness_raw.csv
        '''
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        default=str(default_file),
        help=f'Path to mro_fields_completeness_raw.csv file (default: {default_file.name} in v10)'
    )
    
    args = parser.parse_args()
    
    input_file = Path(args.file)
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    calculate_completeness_summary(input_file)

if __name__ == "__main__":
    main()
