#!/usr/bin/env python3
"""
Count triples in v10 RDF data files and report statistics.

Usage:
    python -m scripts.count_triples
"""

import argparse
import sys
from pathlib import Path
from rdflib import Graph, Namespace
from collections import Counter


def load_and_count(file_path: Path) -> tuple[Graph, int]:
    """Load a Turtle file and return the graph and triple count."""
    if not file_path.exists():
        print(f"  ✗ File not found: {file_path}")
        return None, 0
    
    print(f"Loading {file_path.name}...")
    
    g = Graph()
    g.parse(file_path, format='turtle')
    triple_count = len(g)
    
    file_size_kb = file_path.stat().st_size / 1024
    print(f"  ✓ Loaded ({file_size_kb:.1f} KB, {triple_count:,} triples)")
    
    return g, triple_count


def count_by_type(graph: Graph) -> dict:
    """Count entities by rdf:type."""
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    
    type_counts = Counter()
    
    for s, p, o in graph.triples((None, RDF.type, None)):
        # Extract local name from the type URI
        type_uri = str(o)
        if '#' in type_uri:
            type_name = type_uri.split('#')[-1]
        elif '/' in type_uri:
            type_name = type_uri.split('/')[-1]
        else:
            type_name = type_uri
        type_counts[type_name] += 1
    
    return dict(type_counts)


def count_by_predicate(graph: Graph) -> dict:
    """Count usage of each predicate."""
    predicate_counts = Counter()
    
    for s, p, o in graph:
        pred_uri = str(p)
        if '#' in pred_uri:
            pred_name = pred_uri.split('#')[-1]
        elif '/' in pred_uri:
            pred_name = pred_uri.split('/')[-1]
        else:
            pred_name = pred_uri
        predicate_counts[pred_name] += 1
    
    return dict(predicate_counts)


def main():
    parser = argparse.ArgumentParser(
        description='Count triples in v10 RDF data files and report statistics'
    )
    parser.add_argument(
        '--mappings',
        default='../hse-data/mapping/v10/mappings_final.ttl',
        help='Path to mappings_final.ttl file'
    )
    parser.add_argument(
        '--terminology',
        default='../hse-data/mapping/phpt.ttl',
        help='Path to phpt.ttl terminology file'
    )
    parser.add_argument(
        '--show-predicates',
        action='store_true',
        help='Show predicate usage statistics'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent.parent
    mappings_path = (script_dir / args.mappings).resolve()
    terminology_path = (script_dir / args.terminology).resolve()
    
    print("=" * 60)
    print("RDF Triple Count - v10 Data")
    print("=" * 60)
    print(f"Mappings: {mappings_path}")
    print(f"Terminology: {terminology_path}")
    print("=" * 60)
    print()
    
    # Check if mappings file exists
    if not mappings_path.exists():
        print(f"Error: Mappings file not found: {mappings_path}")
        print("Please run main.v10.sh first to generate the mappings.")
        sys.exit(1)
    
    try:
        # Load mappings file
        print("Loading RDF files...")
        mappings_graph, mappings_count = load_and_count(mappings_path)
        
        if mappings_graph is None:
            sys.exit(1)
        
        total_triples = mappings_count
        
        # Optionally load terminology
        if terminology_path.exists():
            terminology_graph, terminology_count = load_and_count(terminology_path)
            if terminology_graph is not None:
                total_triples += terminology_count
        else:
            print(f"  ⚠ Terminology file not found: {terminology_path}")
        
        print()
        print("=" * 60)
        print(f"Total triples: {total_triples:,}")
        print("=" * 60)
        print()
        
        # Count entities by type
        print("Entity counts by type:")
        type_counts = count_by_type(mappings_graph)
        for type_name, count in sorted(type_counts.items(), key=lambda x: -x[1])[:15]:
            print(f"  {type_name:30s} {count:6,}")
        
        # Optionally show predicate statistics
        if args.show_predicates:
            print()
            print("Top 15 predicates by usage:")
            predicate_counts = count_by_predicate(mappings_graph)
            for pred_name, count in sorted(predicate_counts.items(), key=lambda x: -x[1])[:15]:
                print(f"  {pred_name:30s} {count:6,}")
        
        print()
        print("=" * 60)
        print("✓ Analysis complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
