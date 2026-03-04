#!/usr/bin/env python3
"""Run SPARQL UPDATE queries on RDF files using rdflib."""
import sys
import re
from rdflib import Graph, Namespace

def split_sparql_updates(query_text: str):
    """Split SPARQL UPDATE queries that are separated by semicolons."""
    # Remove comments
    lines = []
    for line in query_text.split('\n'):
        # Remove comments (# to end of line)
        line = re.sub(r'#.*$', '', line)
        lines.append(line)
    query_text = '\n'.join(lines)
    
    # Split by }; pattern which indicates end of an update operation
    # Keep the } as part of the query
    queries = []
    current = []
    
    for line in query_text.split('\n'):
        current.append(line)
        if re.search(r'\}\s*;\s*$', line):
            # End of query found
            query = '\n'.join(current).strip()
            if query and not query.startswith('PREFIX'):
                queries.append(query)
            current = []
    
    # Add any remaining content
    remaining = '\n'.join(current).strip()
    if remaining and not remaining.startswith('PREFIX'):
        queries.append(remaining)
    
    return queries

def run_sparql_update(ttl_file: str, query_file: str, output_file: str):
    """Load a Turtle file, run SPARQL UPDATE, and save the result."""
    
    # Load the Turtle file
    print(f"Loading {ttl_file}...")
    g = Graph()
    g.parse(ttl_file, format='turtle')
    print(f"Loaded {len(g)} triples")
    
    # Read the SPARQL query
    with open(query_file, 'r') as f:
        query_text = f.read()
    
    # Extract PREFIX declarations
    prefix_lines = []
    for line in query_text.split('\n'):
        if line.strip().startswith('PREFIX'):
            prefix_lines.append(line)
    prefixes = '\n'.join(prefix_lines)
    
    # Split into individual update operations
    queries = split_sparql_updates(query_text)
    
    print(f"Found {len(queries)} update operations")
    
    for i, q in enumerate(queries, 1):
        # Add prefixes to each query
        full_query = f"{prefixes}\n\n{q}"
        print(f"Running update {i}/{len(queries)}...")
        try:
            g.update(full_query)
        except Exception as e:
            print(f"Warning: Query {i} failed: {e}")
            print(f"Query was: {q[:100]}...")
    
    # Save the result
    print(f"Saving to {output_file}...")
    g.serialize(destination=output_file, format='turtle')
    print(f"Saved {len(g)} triples")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: run_sparql_update.py <input.ttl> <query.rq> <output.ttl>")
        sys.exit(1)
    
    run_sparql_update(sys.argv[1], sys.argv[2], sys.argv[3])
