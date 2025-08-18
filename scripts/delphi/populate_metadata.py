import argparse
import pandas as pd
import numpy as np

def populate_rule_1(self: pd.Series, compare: pd.Series, col: str) -> pd.Series:
    # Populate metadata for rule 1
    return pd.isna(self[col]) and not pd.isna(compare[col]) and str(self[col]) != str(compare[col])

def main():
    parser = argparse.ArgumentParser(description="Populate metadata")
    parser.add_argument("-d", "--delphi-file", type=str, help="Delphi input file path")
    parser.add_argument("-m", "--metadata-file", type=str, help="Metadata input file path")
    parser.add_argument("-o", "--output", type=str, help="Output file path")
    args = parser.parse_args()

    # TODO: Implement the metadata population logic
    delphi_file = args.delphi_file
    metadata_file = args.metadata_file
    output_file = args.output

    delphi_df = pd.read_csv(delphi_file)
    metadata_df = pd.read_csv(metadata_file)
    metadata_df = metadata_df.assign(
        **{
            "skos:historyNote": np.nan,
            "owl:sameAs": np.nan,
            "Unnamed: 24": np.nan,
            "Unnamed: 25": np.nan
        }
    )
    compare_columns = metadata_df.columns
    print(f'Columns to compare: {compare_columns.tolist()}')
    cso_identifier_list = metadata_df['dct:identifier']

    def mask(ori_id: str) -> bool:
        return cso_identifier_list.apply(lambda x: str(x) in str(ori_id)).any()

    def compare_two_rows(self: pd.Series, compare: pd.Series, index: np.int64) -> pd.Series:
        # Compare two rows and return the differences
        equal = self.equals(compare)
        if equal:
            return True
        else:
            # print(self[compare_columns].compare(compare[compare_columns]))
            for col in compare_columns:
                if populate_rule_1(self, compare, col):
                    print(f"Difference in column '{col}': {self[col]} vs {compare[col]}")
                    delphi_df.at[index, col] = compare[col]
            return False

    # Perform metadata population logic
    for index, row in delphi_df.iterrows():
        original_id = row.get('owl:sameAs')
        delphi_id = row['dct:identifier']

        if original_id:
            found = mask(original_id)
            if found:
                # print(f"Found metadata for {delphi_id}, original: {original_id}, metadata: {found}")
                metadata_row = metadata_df[metadata_df['dct:identifier'] == original_id].iloc[0]
                compare_two_rows(row, metadata_row, index)
                print("\n")
    delphi_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()