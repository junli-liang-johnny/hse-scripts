#!/usr/bin/env python3
"""
Generate a visualization of field completeness from mro_fields_completeness_raw.csv
"""

import argparse
import csv
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("Error: matplotlib is required. Install it with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def visualize_completeness(input_file, output_file=None):
    """Generate bar chart visualization of field completeness"""
    
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
    
    # Prepare data for visualization
    field_types = ['Overall', 'Mandatory', 'Recommended', 'Optional', 'Required\n(Report)']
    percentages = [overall_mean, mandatory_mean, recommended_mean, optional_mean, required_mean]
    counts = [n, n, n, n, n]
    
    # Create figure with dual y-axes
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Set up x-axis
    x = range(len(field_types))
    width = 0.35
    
    # Plot counts (blue bars)
    bars1 = ax1.bar([i - width/2 for i in x], counts, width, label='Count', color='#3498db', alpha=0.8)
    ax1.set_xlabel('Indicator Fields', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Indicators', fontsize=12, fontweight='bold', color='#3498db')
    ax1.tick_params(axis='y', labelcolor='#3498db')
    ax1.set_ylim(0, max(counts) * 1.2)
    
    # Create second y-axis for percentages
    ax2 = ax1.twinx()
    bars2 = ax2.bar([i + width/2 for i in x], percentages, width, label='Percentage', color='#f39c12', alpha=0.8)
    ax2.set_ylabel('Completeness Percentage (%)', fontsize=12, fontweight='bold', color='#f39c12')
    ax2.tick_params(axis='y', labelcolor='#f39c12')
    ax2.set_ylim(0, 100)
    
    # Set x-axis labels
    ax1.set_xticks(x)
    ax1.set_xticklabels(field_types, fontsize=10)
    
    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars1, counts)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'n={count}',
                ha='center', va='bottom', fontsize=9, color='#2c3e50')
    
    for i, (bar, pct) in enumerate(zip(bars2, percentages)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:.1f}%',
                ha='center', va='bottom', fontsize=9, color='#e67e22')
    
    # Add title
    plt.title('Indicator Fields Completeness Summary', fontsize=14, fontweight='bold', pad=20)
    
    # Create custom legend
    blue_patch = mpatches.Patch(color='#3498db', label='Count (blue)', alpha=0.8)
    yellow_patch = mpatches.Patch(color='#f39c12', label='Percentage (yellow)', alpha=0.8)
    ax1.legend(handles=[blue_patch, yellow_patch], loc='upper left', fontsize=10)
    
    # Add grid for better readability
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Visualization saved to: {output_file}")
    else:
        print("\n✓ Displaying visualization...")
        plt.show()
    
    plt.close()


def main():
    """CLI entry point"""
    # Default to v10 output in hse-data directory
    script_dir = Path(__file__).parent
    default_file = script_dir.parent.parent.parent / "hse-data" / "output" / "dq" / "v10" / "mro_fields_completeness_raw.csv"
    default_output = script_dir.parent.parent.parent / "hse-data" / "output" / "dq" / "v10" / "completeness_chart.png"
    
    parser = argparse.ArgumentParser(
        description='Generate visualization of indicator field completeness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use default file (v10) and display chart
  hse-completeness-viz
  
  # Save to specific file
  hse-completeness-viz -o /path/to/output.png
  
  # Use custom input file
  hse-completeness-viz /path/to/mro_fields_completeness_raw.csv -o chart.png
        '''
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        default=str(default_file),
        help=f'Path to mro_fields_completeness_raw.csv file (default: {default_file.name} in v10)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output file path for the chart (PNG format). If not specified, chart will be displayed.'
    )
    
    parser.add_argument(
        '--save-default',
        action='store_true',
        help=f'Save to default location: {default_output}'
    )
    
    args = parser.parse_args()
    
    input_file = Path(args.file)
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    output_file = None
    if args.save_default:
        output_file = default_output
        output_file.parent.mkdir(parents=True, exist_ok=True)
    elif args.output:
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    
    visualize_completeness(input_file, output_file)


if __name__ == "__main__":
    main()
