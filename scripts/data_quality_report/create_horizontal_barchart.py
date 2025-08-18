#!/usr/bin/env python3
"""
Script to create horizontal bar charts for metadata fields count data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import seaborn as sns
from pathlib import Path
import argparse

def create_horizontal_barchart(csv_file_path, output_path=None, chart_type='percentage', color_scheme='Set3', **kwargs):
    """
    Create a horizontal bar chart from metadata fields count CSV.
    
    Args:
        csv_file_path (str): Path to the CSV file
        output_path (str): Path to save the chart (optional)
        chart_type (str): Type of chart - 'percentage', 'count', or 'both'
        color_scheme (str): Color scheme for bars - 'Set3', 'tab20', 'viridis', 'plasma', 'rainbow', etc.
    """
    x_axis_label = kwargs.get('x_label', 'Completeness Percent (%)')
    show_avg = kwargs.get('show_avg', True)
    
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    # Sort by percentage for better visualization
    df_sorted = df.sort_values(x_axis_label, ascending=True)

    # Compute average percentage (coerce to numeric in case of stray strings)
    try:
        avg_pct = pd.to_numeric(df_sorted[x_axis_label], errors='coerce').mean()
    except Exception:
        avg_pct = None
    
    # Set up the plot style
    plt.style.use('default')
    
    # Create a color palette with different colors for each bar
    n_bars = len(df_sorted)
    cmap = mpl.colormaps.get_cmap(color_scheme)
    colors = cmap(np.linspace(0, 1, n_bars))
    
    if chart_type == 'percentage':
        # Create horizontal bar chart for percentages
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(df_sorted['Metadata Field'], df_sorted[x_axis_label], color=colors)
        
        # Customize the chart
        ax.set_xlabel(x_axis_label, fontsize=12, fontweight='bold')
        ax.set_ylabel('Metadata Field', fontsize=12, fontweight='bold')
        ax.set_title('Metadata Fields Coverage - Percentage Distribution', 
                    fontsize=14, fontweight='bold', pad=20)
        
    # Add percentage labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                   f'{width:.1f}%', ha='left', va='center', fontweight='bold')
        
        # Set x-axis limit to accommodate labels
        ax.set_xlim(0, 110)

    # Add average percentage annotation at top-left
    if show_avg and avg_pct is not None:
        ax.text(0.01, 0.98, f'Avg: {avg_pct:.1f}%', transform=ax.transAxes,
            ha='left', va='top', fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3))
        
    elif chart_type == 'count':
        # Create horizontal bar chart for counts
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(df_sorted['Metadata Field'], df_sorted['Present Count'], color=colors)
        
        # Customize the chart
        ax.set_xlabel('Present Count', fontsize=12, fontweight='bold')
        ax.set_ylabel('Metadata Field', fontsize=12, fontweight='bold')
        ax.set_title('Metadata Fields Coverage - Count Distribution', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add count labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 5, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        # Set x-axis limit to accommodate labels
        ax.set_xlim(0, max(df_sorted['Present Count']) * 1.15)
        
    elif chart_type == 'both':
        # Create side-by-side horizontal bar charts
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Percentage chart
        bars1 = ax1.barh(df_sorted['Metadata Field'], df_sorted[x_axis_label], color=colors)
        ax1.set_xlabel(x_axis_label, fontsize=12, fontweight='bold')
        ax1.set_ylabel('Metadata Field', fontsize=12, fontweight='bold')
        ax1.set_title('Coverage Percentage', fontsize=14, fontweight='bold')
        
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}%', ha='left', va='center', fontweight='bold')
        ax1.set_xlim(0, 110)

        # Add average percentage annotation on percentage subplot
        if show_avg and avg_pct is not None:
            ax1.text(0.01, 0.98, f'Avg: {avg_pct:.1f}%', transform=ax1.transAxes,
                     ha='left', va='top', fontweight='bold',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3))
        
        # Count chart
        bars2 = ax2.barh(df_sorted['Metadata Field'], df_sorted['Present Count'], color=colors)
        ax2.set_xlabel('Present Count', fontsize=12, fontweight='bold')
        ax2.set_ylabel('')  # Remove y-label for second chart
        ax2.set_title('Present Count', fontsize=14, fontweight='bold')
        
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width + 5, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontweight='bold')
        ax2.set_xlim(0, max(df_sorted['Present Count']) * 1.15)
        
        plt.suptitle('Metadata Fields Coverage Analysis', fontsize=16, fontweight='bold')
    
    # Improve layout
    plt.tight_layout()
    
    # Add grid for better readability
    if chart_type != 'both':
        ax.grid(axis='x', alpha=0.3, linestyle='--')
    else:
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Save the chart if output path is provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Chart saved to: {output_path}")
    
    # Show the chart
    plt.show()
    
    return fig

def main():
    parser = argparse.ArgumentParser(description='Create horizontal bar chart from metadata CSV')
    parser.add_argument('-i', '--input', help='Path to the CSV file')
    parser.add_argument('-o', '--output', help='Output file path for saving the chart')
    parser.add_argument('-t', '--type', choices=['percentage', 'count', 'both'], 
                       default='percentage', help='Type of chart to create')
    parser.add_argument('-c', '--colors', default='Set3',
                       help='Color scheme for bars (Set3, tab20, viridis, plasma, rainbow, etc.)')
    parser.add_argument('--no-avg', action='store_true', help='Disable average percentage annotation')
    
    args = parser.parse_args()
    
    # Create the chart
    create_horizontal_barchart(
        args.input,
        args.output,
        args.type,
        args.colors,
        show_avg=not args.no_avg
    )

if __name__ == "__main__":
    main()
