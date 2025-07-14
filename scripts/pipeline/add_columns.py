# this script combines DataFrames horizontally, creating rows where each DataFrame becomes one row

import pandas as pd
import argparse

def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Combine two datasets horizontally as separate rows with all columns.')
    parser.add_argument('--primary', type=str, required=True, help='Path to the first dataset')
    parser.add_argument('--secondary', type=str, required=True, help='Path to the second dataset')
    parser.add_argument('--output', type=str, default='combined_datasets.csv', help='Output file path')
    parser.add_argument('--fill-value', type=str, default='', help='Value to fill missing columns (default: empty string)')
    parser.add_argument('--sort', action='store_true', help='Sort columns alphabetically in the output')
    args = parser.parse_args()

    # load the datasets
    print(f"Loading first dataset: {args.primary}")
    primary_df = pd.read_csv(args.primary)
    print(f"First dataset shape: {primary_df.shape}")
    print(f"First dataset columns: {primary_df.columns.tolist()}")
    
    print(f"\nLoading second dataset: {args.secondary}")
    secondary_df = pd.read_csv(args.secondary)
    print(f"Second dataset shape: {secondary_df.shape}")
    print(f"Second dataset columns: {secondary_df.columns.tolist()}")
    
    # Get all unique columns from both DataFrames
    # Order: primary_df columns first, then secondary_df columns not in primary_df
    all_columns = list(primary_df.columns)
    secondary_only_columns = [col for col in secondary_df.columns if col not in primary_df.columns]
    all_columns.extend(secondary_only_columns)
    
    if args.sort:
        all_columns.sort()
    
    print(f"\nAll unique columns: {all_columns}")
    
    # Create a result DataFrame with all columns
    result_data = []

    for _, row in primary_df.iterrows():
        primary_row = {}
        for col in all_columns:
            if col in primary_df.columns:
                primary_row[col] = row[col]
            else:
                primary_row[col] = args.fill_value
        result_data.append(primary_row)

    for _, row in secondary_df.iterrows():
        secondary_row = {}
        for col in all_columns:
            if col in secondary_df.columns:
                secondary_row[col] = row[col]
            else:
                secondary_row[col] = args.fill_value
        result_data.append(secondary_row)
    
    # Create the result DataFrame
    result = pd.DataFrame(result_data, columns=all_columns)
    
    print(f"Result shape: {result.shape}")
    print(f"Result columns: {result.columns.tolist()}")
    
    # Save the result
    result.to_csv(args.output, index=False)
    print(f"\nResult saved to: {args.output}")
    
    # Display the result
    print(f"\nResult DataFrame:")
    print(result)

if __name__ == "__main__":
    main()