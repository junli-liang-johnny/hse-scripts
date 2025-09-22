import argparse
import pandas as pd

def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Reorder columns in a CSV file.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output', type=str, default='reordered_output.csv', help='Output file path')
    parser.add_argument('--columns', type=str, nargs='+', help='Specific column order (space-separated)')
    parser.add_argument('--sort', choices=['asc', 'desc'], help='Sort columns alphabetically (asc/desc)')
    parser.add_argument('--move-to-front', type=str, nargs='+', help='Move specific columns to the front')
    parser.add_argument('--move-to-end', type=str, nargs='+', help='Move specific columns to the end')
    args = parser.parse_args()

    # Load the CSV file
    print(f"Loading CSV file: {args.input}")
    df = pd.read_csv(args.input)
    print(f"Original shape: {df.shape}")
    print(f"Original columns: {df.columns.tolist()}")

    # Apply reordering based on arguments
    if args.columns:
        # Use specific column order
        print(f"\nReordering to specific order: {args.columns}")
        # Validate that all specified columns exist
        missing_cols = [col for col in args.columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in dataset: {missing_cols}")
        # Check if all columns are specified
        if len(args.columns) != len(df.columns):
            extra_cols = [col for col in df.columns if col not in args.columns]
            if extra_cols:
                print(f"Warning: These columns will be dropped: {extra_cols}")
        df = df[args.columns]
        
    elif args.sort:
        # Sort columns alphabetically
        if args.sort == 'asc':
            print("\nSorting columns alphabetically (ascending)")
            df = df.reindex(sorted(df.columns), axis=1)
        else:
            print("\nSorting columns alphabetically (descending)")
            df = df.reindex(sorted(df.columns, reverse=True), axis=1)
            
    elif args.move_to_front:
        # Move specific columns to front
        print(f"\nMoving columns to front: {args.move_to_front}")
        cols = df.columns.tolist()
        # Remove the columns to move from their current position
        for col in args.move_to_front:
            if col in cols:
                cols.remove(col)
        # Add them to the front
        new_order = args.move_to_front + cols
        df = df[new_order]
        
    elif args.move_to_end:
        # Move specific columns to end
        print(f"\nMoving columns to end: {args.move_to_end}")
        cols = df.columns.tolist()
        # Remove the columns to move from their current position
        for col in args.move_to_end:
            if col in cols:
                cols.remove(col)
        # Add them to the end
        new_order = cols + args.move_to_end
        df = df[new_order]
        
    else:
        print("\nNo reordering specified. Use --help to see options.")
        return

    print(f"\nNew column order: {df.columns.tolist()}")
    
    # Save the reordered DataFrame
    df.to_csv(args.output, index=False)
    print(f"Reordered CSV saved to: {args.output}")
    
    # Display sample
    print(f"\nFirst 5 rows of reordered data:")
    print(df.head())

if __name__ == "__main__":
    main()