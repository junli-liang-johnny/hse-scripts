#!/usr/bin/env python3
"""
Generate static HTML pages for indicators, indicator groups, and datasets from mappings_final.ttl
"""

import os
import shutil
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, DCTERMS, SKOS, OWL, XSD
from urllib.parse import urlparse
import html

# Define namespaces
DCAT = Namespace("http://www.w3.org/ns/dcat#")
PHI = Namespace("https://w3id.org/hse/ontology/phi#")
PHD = Namespace("https://w3id.org/hse/ontology/phd#")
PHT = Namespace("https://w3id.org/hse/terminology#")
HEALTHDCATAP = Namespace("http://healthdata.dublinked.ie/def/healthdcatap#")
DPV = Namespace("https://w3id.org/dpv#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")


def extract_id_from_uri(uri):
    """Extract the ID from a URI (e.g., hse0000016 from https://w3id.org/hse/indicator/hse0000016)"""
    return str(uri).split('/')[-1]


def format_value(value, g):
    """Format an RDF value for HTML display"""
    if isinstance(value, URIRef):
        # If it's a URI, create a link
        uri_str = str(value)
        label = get_label(value, g) or extract_id_from_uri(value)
        if uri_str.startswith('https://w3id.org/hse/'):
            # Internal link - make it relative
            if '/indicator/' in uri_str:
                return f'<a href="/hse-data-portal/indicator/{extract_id_from_uri(value)}">{html.escape(label)}</a>'
            elif '/indicator-group/' in uri_str:
                return f'<a href="/hse-data-portal/indicator-group/{extract_id_from_uri(value)}">{html.escape(label)}</a>'
            elif '/dataset/' in uri_str:
                return f'<a href="/hse-data-portal/dataset/{extract_id_from_uri(value)}">{html.escape(label)}</a>'
        return f'<a href="{html.escape(uri_str)}" target="_blank">{html.escape(label)}</a>'
    elif isinstance(value, Literal):
        return html.escape(str(value))
    return html.escape(str(value))


def get_label(uri, g):
    """Get a human-readable label for a URI"""
    # Try different label properties
    for pred in [DCTERMS.title, RDFS.label, SKOS.prefLabel]:
        label = g.value(uri, pred)
        if label:
            return str(label)
    return None


def generate_html_page(resource_uri, resource_type, g, output_dir):
    """Generate an HTML page for a single resource"""
    
    resource_id = extract_id_from_uri(resource_uri)
    title = g.value(resource_uri, DCTERMS.title) or resource_id
    
    # HTML template matching browser.html styling
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(str(title))} - HSE Data Portal</title>
    <!-- Password Protection -->
    <script src="../../auth.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            line-height: 1.6;
        }}

        header {{
            background: #007acc;
            color: white;
            padding: 1.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .home-button {{
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .home-button:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}

        .content {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 2rem auto;
            max-width: 1400px;
        }}

        .back-button {{
            display: inline-block;
            margin-bottom: 1.5rem;
            padding: 0.5rem 1rem;
            background: #f0f0f0;
            color: #333;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
        }}

        .back-button:hover {{
            background: #e0e0e0;
        }}

        .detail-title {{
            color: #007acc;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #007acc;
        }}

        .detail-uri {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1.5rem;
            word-break: break-all;
        }}

        .properties-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}

        .properties-table th {{
            background: #f8f9fa;
            padding: 0.75rem;
            text-align: left;
            border: 1px solid #dee2e6;
            color: #007acc;
            font-weight: 600;
        }}

        .properties-table td {{
            padding: 0.75rem;
            border: 1px solid #dee2e6;
            vertical-align: top;
        }}

        .properties-table tr:hover {{
            background: #f8f9fa;
        }}

        .property-label {{
            font-weight: 500;
            color: #495057;
            min-width: 200px;
        }}

        .property-value {{
            color: #212529;
        }}

        .property-value a {{
            color: #007acc;
            text-decoration: none;
        }}

        .property-value a:hover {{
            text-decoration: underline;
        }}

        footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Health Population Data Browser</h1>
            <p class="subtitle">Explore indicators, datasets, and indicator groups</p>
            <a href="../../browser.html" class="home-button">← Back to Browser</a>
        </div>
    </header>

    <div class="container">
        <main class="content">
            <a href="../../browser.html" class="back-button">← Back to list</a>
            <h2 class="detail-title">{html.escape(str(title))}</h2>
            <div class="detail-uri">{html.escape(str(resource_uri))}</div>
            
            <h3>Properties</h3>
            <table class="properties-table">
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # Add resource type
    types = list(g.objects(resource_uri, RDF.type))
    if types:
        type_values = '<br>'.join([format_value(rdf_type, g) for rdf_type in types])
        html_content += f'''
                    <tr>
                        <td class="property-label">Type</td>
                        <td class="property-value">{type_values}</td>
                    </tr>'''
    
    # Define properties to display with their labels
    properties = [
        (DCTERMS.identifier, "Identifier"),
        (DCTERMS.title, "Title"),
        (SKOS.definition, "Definition"),
        (RDFS.comment, "Comment"),
        (SKOS.note, "Note"),
        (PHI.Rationale, "Rationale"),
        (PHI.indicatorType, "Indicator Type"),
        (PHI.status, "Status"),
        (DCTERMS.accrualPeriodicity, "Update Frequency"),
        (HEALTHDCATAP.healthTheme, "Health Theme"),
        (DC.spatial, "Geographic Coverage"),
        (PHD.spatialAggregation, "Spatial Aggregation"),
        (DCTERMS.accessRights, "Access Rights"),
        (DCTERMS.creator, "Creator"),
        (DCTERMS.publisher, "Publisher"),
        (DCTERMS.provenance, "Provenance"),
        (PHI.numeratorDataElement, "Numerator Data Element"),
        (PHI.numeratorSource, "Numerator Source"),
        (PHI.denominatorDataElement, "Denominator Data Element"),
        (PHI.denominatorSource, "Denominator Source"),
        (PHI.disaggregation, "Disaggregation"),
        (PHI.memberOfGroup, "Member Of Group"),
        (DCAT.distribution, "Distribution"),
        (DCAT.temporalResolution, "Temporal Resolution"),
        (DPV.hasDataController, "Data Controller"),
        (DPV.hasPersonalData, "Personal Data Type"),
        (HEALTHDCATAP.hdab, "Health Data Access Body"),
        (HEALTHDCATAP.minTypicalAge, "Minimum Typical Age"),
        (HEALTHDCATAP.maxTypicalAge, "Maximum Typical Age"),
        (OWL.sameAs, "Same As"),
    ]
    
    # Display all properties
    for pred, label in properties:
        values = list(g.objects(resource_uri, pred))
        if values:
            value_html = '<br>'.join([format_value(value, g) for value in values])
            html_content += f'''
                    <tr>
                        <td class="property-label">{html.escape(label)}</td>
                        <td class="property-value">{value_html}</td>
                    </tr>'''
    
    # For indicator groups, show members
    if resource_type == "indicator-group":
        members = list(g.subjects(PHI.memberOfGroup, resource_uri))
        if members:
            member_html = '<br>'.join([format_value(member, g) for member in members])
            html_content += f'''
                    <tr>
                        <td class="property-label">Contains Indicators</td>
                        <td class="property-value">{member_html}</td>
                    </tr>'''
    
    html_content += '''
                </tbody>
            </table>
        </main>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2026 Health Service Executive. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
'''
    
    # Write the file
    output_path = Path(output_dir) / resource_type / resource_id / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding='utf-8')
    print(f"Generated: {output_path}")


def clean_output_directories(output_dir):
    """Clean existing output directories"""
    for dir_name in ['indicator', 'indicator-group', 'dataset']:
        dir_path = Path(output_dir) / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Cleaned: {dir_path}")


def main():
    """Main function to generate static pages from TTL file"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate static HTML pages from RDF TTL file')
    parser.add_argument('--ttl-file', required=True, help='Path to the input TTL file')
    parser.add_argument('--output-dir', required=True, help='Directory to output the generated HTML files')
    
    args = parser.parse_args()
    
    ttl_file = Path(args.ttl_file)
    output_dir = Path(args.output_dir)
    
    if not ttl_file.exists():
        print(f"❌ Error: TTL file not found: {ttl_file}")
        return 1
    
    print(f"Loading RDF data from {ttl_file}...")
    
    # Load the TTL file
    g = Graph()
    g.parse(str(ttl_file), format='turtle')
    
    # Bind namespaces for cleaner output
    g.bind('dcat', DCAT)
    g.bind('phi', PHI)
    g.bind('phd', PHD)
    g.bind('pht', PHT)
    g.bind('dcterms', DCTERMS)
    g.bind('healthdcatap', HEALTHDCATAP)
    g.bind('dpv', DPV)
    g.bind('dc', DC)
    
    print(f"Loaded {len(g)} triples")
    
    # Clean existing directories
    print("\nCleaning existing directories...")
    clean_output_directories(output_dir)
    
    # Generate pages for indicators
    print("\nGenerating indicator pages...")
    indicators = list(g.subjects(RDF.type, PHI.Indicator))
    for indicator_uri in indicators:
        generate_html_page(indicator_uri, "indicator", g, output_dir)
    
    print(f"Generated {len(indicators)} indicator pages")
    
    # Generate pages for indicator groups
    print("\nGenerating indicator group pages...")
    indicator_groups = list(g.subjects(RDF.type, PHI.IndicatorGroup))
    for group_uri in indicator_groups:
        generate_html_page(group_uri, "indicator-group", g, output_dir)
    
    print(f"Generated {len(indicator_groups)} indicator group pages")
    
    # Generate pages for datasets (excluding indicators which are also datasets)
    print("\nGenerating dataset pages...")
    all_datasets = set(g.subjects(RDF.type, DCAT.Dataset))
    datasets = all_datasets - set(indicators)  # Exclude indicators
    
    for dataset_uri in datasets:
        generate_html_page(dataset_uri, "dataset", g, output_dir)
    
    print(f"Generated {len(datasets)} dataset pages")
    
    print("\n✅ All static pages generated successfully!")
    print(f"\nTotal pages created: {len(indicators) + len(indicator_groups) + len(datasets)}")
    
    return 0


if __name__ == "__main__":
    exit(main())
