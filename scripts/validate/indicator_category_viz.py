#!/usr/bin/env python3
"""
Generate a visualization of field category completeness for each indicator
Shows Report Required, Mandatory, Recommended, Optional, and Overall percentages per indicator
"""

import argparse
import csv
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError as e:
    print(f"Error: Required library not found: {e}", file=sys.stderr)
    print("Install with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def extract_indicator_id(indicator_uri):
    """Extract indicator ID (e.g., hse0000009) from URI"""
    if '/' in indicator_uri:
        return indicator_uri.split('/')[-1]
    return indicator_uri


def load_completeness_data(csv_file):
    """
    Load completeness data from CSV file
    Returns a list of dictionaries with indicator info
    """
    data = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert percentage strings to floats
            try:
                data.append({
                    'indicator': row['indicator'],
                    'indicator_id': extract_indicator_id(row['indicator']),
                    'title': row.get('title', ''),
                    'required': float(row['requiredFieldCompletenessPercent'].rstrip('%')) if row.get('requiredFieldCompletenessPercent') else 0,
                    'mandatory': float(row['mandatoryCompletenessPercent'].rstrip('%')) if row.get('mandatoryCompletenessPercent') else 0,
                    'recommended': float(row['recommendedCompletenessPercent'].rstrip('%')) if row.get('recommendedCompletenessPercent') else 0,
                    'optional': float(row['optionalCompletenessPercent'].rstrip('%')) if row.get('optionalCompletenessPercent') else 0,
                    'overall': float(row['overallCompletenessPercent'].rstrip('%')) if row.get('overallCompletenessPercent') else 0
                })
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row due to error: {e}", file=sys.stderr)
                continue
    
    return data


def visualize_category_completeness(data, output_file=None, chart_type='line', show_labels=False):
    """
    Create visualization of category completeness per indicator
    
    Args:
        data: List of dictionaries with completeness data
        output_file: Path to save the chart (if None, displays instead)
        chart_type: 'line' or 'bar'
        show_labels: Whether to show indicator IDs on x-axis
    """
    if not data:
        print("Error: No data to visualize", file=sys.stderr)
        return
    
    # Extract data for plotting
    indicator_ids = [d['indicator_id'] for d in data]
    required = [d['required'] for d in data]
    mandatory = [d['mandatory'] for d in data]
    recommended = [d['recommended'] for d in data]
    optional = [d['optional'] for d in data]
    overall = [d['overall'] for d in data]
    
    # Create figure with appropriate size
    num_indicators = len(indicator_ids)
    fig_width = max(12, num_indicators * 0.3)
    fig_height = 8
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # X-axis positions
    x = range(len(indicator_ids))
    
    if chart_type == 'line':
        # Line chart
        ax.plot(x, required, marker='o', linewidth=2, markersize=4, label='Report Required Fields', color='#e74c3c')
        ax.plot(x, mandatory, marker='s', linewidth=2, markersize=4, label='Mandatory Fields', color='#3498db')
        ax.plot(x, recommended, marker='^', linewidth=2, markersize=4, label='Recommended Fields', color='#2ecc71')
        ax.plot(x, optional, marker='d', linewidth=2, markersize=4, label='Optional Fields', color='#f39c12')
        ax.plot(x, overall, marker='*', linewidth=2.5, markersize=6, label='Overall Fields', color='#9b59b6')
    else:
        # Grouped bar chart
        bar_width = 0.15
        x_pos = list(x)
        
        ax.bar([i - 2*bar_width for i in x_pos], required, bar_width, label='Report Required Fields', color='#e74c3c', alpha=0.8)
        ax.bar([i - bar_width for i in x_pos], mandatory, bar_width, label='Mandatory Fields', color='#3498db', alpha=0.8)
        ax.bar(x_pos, recommended, bar_width, label='Recommended Fields', color='#2ecc71', alpha=0.8)
        ax.bar([i + bar_width for i in x_pos], optional, bar_width, label='Optional Fields', color='#f39c12', alpha=0.8)
        ax.bar([i + 2*bar_width for i in x_pos], overall, bar_width, label='Overall Fields', color='#9b59b6', alpha=0.8)
    
    # Set labels and title
    ax.set_xlabel('Indicators', fontsize=12, fontweight='bold')
    ax.set_ylabel('Completeness Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'Field Category Completeness by Indicator\n({num_indicators} indicators)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Set y-axis range
    ax.set_ylim(0, 105)
    ax.set_yticks(range(0, 101, 10))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # X-axis labels
    if show_labels and num_indicators <= 50:
        ax.set_xticks(x)
        ax.set_xticklabels(indicator_ids, rotation=90, fontsize=8)
    else:
        # For many indicators, show every nth label or no labels
        if num_indicators <= 100:
            step = max(1, num_indicators // 20)
            ax.set_xticks([i for i in x if i % step == 0])
            ax.set_xticklabels([indicator_ids[i] for i in x if i % step == 0], rotation=90, fontsize=8)
        else:
            ax.set_xticks([])
            ax.set_xlabel(f'Indicators (n={num_indicators})', fontsize=12, fontweight='bold')
    
    # Legend
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    
    # Add 100% reference line
    ax.axhline(y=100, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    
    # Tight layout
    plt.tight_layout()
    
    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Chart saved to: {output_file}")
    else:
        plt.show()
    
    plt.close()


def main():
    # Get script directory for default paths
    script_dir = Path(__file__).parent
    default_file = script_dir.parent.parent.parent / "hse-data" / "output" / "dq" / "v10" / "mro_fields_completeness.csv"
    
    parser = argparse.ArgumentParser(
        description='Generate visualization of field category completeness for each indicator',
        epilog="""
Examples:
  # Generate line chart with default settings
  hse-indicator-viz
  
  # Generate bar chart and save to default location
  hse-indicator-viz --type bar --save-default
  
  # Specify custom input and output files
  hse-indicator-viz -i /path/to/mro_fields_completeness.csv -o chart.png
  
  # Show indicator IDs on x-axis (for smaller datasets)
  hse-indicator-viz --show-labels
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        help=f'Path to mro_fields_completeness.csv file (default: {default_file.name} in v10)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path for the chart (PNG format)'
    )
    
    parser.add_argument(
        '--save-default',
        action='store_true',
        help='Save chart to default location in v10 output directory'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['line', 'bar'],
        default='line',
        help='Chart type: line or bar (default: line)'
    )
    
    parser.add_argument(
        '--show-labels',
        action='store_true',
        help='Show indicator IDs on x-axis (recommended for ≤50 indicators)'
    )
    
    args = parser.parse_args()
    
    # Determine input file
    if args.input:
        csv_file = Path(args.input)
    else:
        csv_file = default_file
    
    if not csv_file.exists():
        print(f"Error: Input file not found: {csv_file}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output file
    output_file = None
    if args.output:
        output_file = Path(args.output)
    elif args.save_default:
        output_dir = script_dir.parent.parent.parent / "hse-data" / "output" / "dq" / "v10"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "indicator_category_completeness_chart.png"
    
    # Load data
    print(f"Loading data from: {csv_file}")
    data = load_completeness_data(csv_file)
    print(f"Loaded {len(data)} indicators")
    
    # Generate visualization
    visualize_category_completeness(
        data, 
        output_file=output_file,
        chart_type=args.type,
        show_labels=args.show_labels
    )


if __name__ == '__main__':
    main()
