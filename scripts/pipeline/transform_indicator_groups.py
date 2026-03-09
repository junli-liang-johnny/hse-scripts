#!/usr/bin/env python3
"""
Transform indicator_groups.csv to add IDs and extract memberOfGroup relationships.
"""
import csv
import sys


def normalize_whitespace(text: str) -> str:
    """Normalize newlines and multiple spaces to single spaces."""
    if not text:
        return text
    # Replace newlines and tabs with spaces, then collapse multiple spaces
    return ' '.join(text.split())


def transform_indicator_groups(input_path: str, output_path: str, relationships_path: str):
    """
    Transform indicator_groups.csv:
    1. Add an 'id' column with full IRIs based on dct:identifier
    2. Remove phi:memberOfGroup column (relationships extracted to separate file)
    3. Create a separate relationships CSV with group-member mappings
    4. Normalize whitespace in provenance fields to match ProvenanceStatement labels
    """
    relationships = []
    provenance_column = 'dct:provenance [a dct:ProvenanceStatement; rdfs:label ]'
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        # New fieldnames without phi:memberOfGroup
        fieldnames = ['id'] + [f for f in reader.fieldnames if f != 'phi:memberOfGroup']
        
        rows = []
        for row in reader:
            # Generate ID from dct:identifier
            identifier = row.get('dct:identifier', '').strip()
            if not identifier:
                continue
            
            group_iri = f'https://hse.ie/data/id/{identifier}'
            row['id'] = group_iri
            
            # Normalize whitespace in provenance field to ensure SPARQL matching works
            if provenance_column in row and row[provenance_column]:
                row[provenance_column] = normalize_whitespace(row[provenance_column])
            
            # Extract member relationships
            members = row.get('phi:memberOfGroup', '').strip()
            if members:
                for member_id in members.split(','):
                    member_id = member_id.strip()
                    if member_id:
                        relationships.append({
                            'group_id': group_iri,
                            'member_id': f'https://hse.ie/data/id/{member_id}'
                        })
            
            # Remove memberOfGroup from row
            row.pop('phi:memberOfGroup', None)
            rows.append(row)
    
    # Write main output
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Write relationships output
    with open(relationships_path, 'w', encoding='utf-8', newline='') as relfile:
        writer = csv.DictWriter(relfile, fieldnames=['group_id', 'member_id'])
        writer.writeheader()
        writer.writerows(relationships)
    
    print(f"Transformed {len(rows)} indicator group records")
    print(f"Extracted {len(relationships)} member relationships")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: transform_indicator_groups.py <input_csv> <output_csv> <relationships_csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    relationships_file = sys.argv[3]
    
    transform_indicator_groups(input_file, output_file, relationships_file)
