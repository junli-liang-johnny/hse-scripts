#!/usr/bin/env python3
"""
inject_skos_metadata.py

Reads a SKOS ConceptScheme from a Turtle (.ttl) file and injects a rendered
metadata section into a SKOS-Play generated index.html.

Usage:
    python inject_skos_metadata.py <terms.ttl> <index.html> [--output <out.html>]

If --output is omitted, the input index.html is updated in-place.

The script looks for a <div class="metadata"> block in the HTML and replaces it.
If none exists, it inserts the metadata block just before the first
<div class="display"> or <div class="abbreviations"> block, or before </body>.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import DCTERMS, FOAF, OWL, RDF, SKOS, XSD

BIBO = Namespace("http://purl.org/ontology/bibo/")


def parse_date(value) -> str:
    """Try to parse a date literal and return a human-readable string."""
    if value is None:
        return ""
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%-d %B %Y")
        except ValueError:
            pass
    return s


def get_one(g: Graph, subject, predicate):
    """Return the first object for a subject/predicate pair, or None."""
    for obj in g.objects(subject, predicate):
        return obj
    return None


def get_all(g: Graph, subject, predicate):
    """Return all objects for a subject/predicate pair as a sorted list."""
    return sorted(str(o) for o in g.objects(subject, predicate))


def build_metadata_html(g: Graph, scheme_uri: URIRef) -> str:
    """Build the metadata <div> HTML from the ConceptScheme triples."""

    def val(pred):
        return get_one(g, scheme_uri, pred)

    def vals(pred):
        return get_all(g, scheme_uri, pred)

    title        = str(val(DCTERMS.title) or val(SKOS.prefLabel) or "Terminology")
    abstract_raw = str(val(DCTERMS.abstract) or val(DCTERMS.description) or "")
    # The abstract may have a literal \n — split on it for paragraphs
    abstract_paras = [p.strip() for p in re.split(r'\\n|\n', abstract_raw) if p.strip()]

    version_uri  = val(OWL.versionInfo)
    prior_uri    = val(OWL.priorVersion)
    version_str  = str(version_uri).rstrip("/").split("/")[-1] if version_uri else ""
    status       = str(val(BIBO.status) or "")
    created      = parse_date(val(DCTERMS.created))
    modified     = parse_date(val(DCTERMS.modified))
    creator      = str(val(DCTERMS.creator) or "")
    contributors = vals(DCTERMS.contributor)
    publisher    = str(val(DCTERMS.publisher) or "")
    source       = str(val(DCTERMS.source) or "")
    license_uri  = val(DCTERMS.license)
    rights_raw   = str(val(DCTERMS.rights) or "")
    homepage     = val(FOAF.homepage)

    # Derive namespace prefix from the scheme URI
    scheme_str = str(scheme_uri)
    ns_uri = scheme_str.rsplit("#", 1)[0] + "#" if "#" in scheme_str else scheme_str.rsplit("/", 1)[0] + "/"
    # Try to find declared prefix in graph
    ns_prefix = ""
    for prefix, namespace in g.namespaces():
        if str(namespace) == ns_uri and prefix:
            ns_prefix = prefix
            break

    lines = []
    lines.append('<div class="metadata">')
    lines.append(f'  <h2>{title}</h2>')

    if version_uri:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>This version:</strong> <a href="{version_uri}">{version_uri}</a>')
        lines.append('  </div>')

    if prior_uri:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Prior version:</strong> <a href="{prior_uri}">{prior_uri}</a>')
        lines.append('  </div>')

    if version_str:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Version information:</strong> {version_str}')
        lines.append('  </div>')

    if status:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Status:</strong> {status}')
        lines.append('  </div>')

    if created:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Date created:</strong> {created}')
        lines.append('  </div>')

    if modified:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Date modified:</strong> {modified}')
        lines.append('  </div>')

    if creator:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Creator:</strong> {creator}')
        lines.append('  </div>')

    if contributors:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Contributors:</strong> {"; ".join(contributors)}')
        lines.append('  </div>')

    if publisher:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Publisher:</strong> {publisher}')
        lines.append('  </div>')

    if source:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Source:</strong> {source}')
        lines.append('  </div>')

    if ns_prefix:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Preferred namespace prefix:</strong> {ns_prefix}')
        lines.append('  </div>')

    if ns_uri:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Preferred namespace URI:</strong> <a href="{ns_uri}">{ns_uri}</a>')
        lines.append('  </div>')

    if license_uri:
        license_label = "Creative Commons Attribution 4.0 International (CC BY 4.0)" \
            if "by/4.0" in str(license_uri) else str(license_uri)
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>License:</strong> <a href="{license_uri}" target="_blank">{license_label}</a>')
        lines.append('  </div>')

    if rights_raw:
        # Normalise copyright symbol
        rights_html = rights_raw.replace("©", "&copy;").replace("–", "&ndash;").replace("—", "&mdash;")
        # Strip trailing sentence about licence (often redundant with the licence field)
        rights_html = re.sub(r'\s*This work is licensed under.*$', '', rights_html).strip()
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Rights:</strong> {rights_html}')
        lines.append('  </div>')

    if homepage:
        lines.append('  <div class="metadata-item">')
        lines.append(f'    <strong>Visualization:</strong> <a href="visualize.html">Tree View</a> &ndash; Interactive hierarchical visualization')
        lines.append('  </div>')

    lines.append('</div>')

    # Build abstract block separately (goes before metadata)
    abstract_html = ['<div class="abstract">']
    abstract_html.append('  <h2>Abstract</h2>')
    for para in abstract_paras:
        abstract_html.append(f'  <p>{para}</p>')
    abstract_html.append('</div>')

    return "\n".join(abstract_html) + "\n\n" + "\n".join(lines)


def _remove_div_block(html: str, class_name: str) -> str:
    """Remove the first <div class="class_name">...</div> block from html."""
    pattern = re.compile(
        r'\s*<div class="' + re.escape(class_name) + r'">.*?</div>',
        re.DOTALL
    )
    return pattern.sub('', html, count=1)


def inject(html: str, metadata_html: str) -> str:
    """Replace existing metadata/abstract blocks, or insert before display/body."""

    # Remove any existing abstract, abbreviations, and metadata divs
    has_abstract = bool(re.search(r'<div class="abstract">', html))
    has_meta = bool(re.search(r'<div class="metadata">', html))

    if has_abstract:
        html = _remove_div_block(html, 'abstract')
    if has_meta:
        html = _remove_div_block(html, 'metadata')

    # Find a good insertion point: just before <div class="abbreviations"> or
    # <div class="display"> or </body>, whichever comes first
    for marker in ['<div class="abbreviations">', '<div class="display">', '</body>']:
        idx = html.find(marker)
        if idx != -1:
            return html[:idx] + metadata_html + "\n\n    " + html[idx:]

    return html + "\n" + metadata_html


def main():
    parser = argparse.ArgumentParser(description="Inject SKOS ConceptScheme metadata into SKOS-Play HTML")
    parser.add_argument("ttl", help="Path to the Turtle file (e.g. terms-1.0.1.ttl)")
    parser.add_argument("html", help="Path to the SKOS-Play index.html")
    parser.add_argument("--output", "-o", help="Output path (default: overwrite html in-place)")
    args = parser.parse_args()

    ttl_path = Path(args.ttl)
    html_path = Path(args.html)
    out_path = Path(args.output) if args.output else html_path

    if not ttl_path.exists():
        print(f"ERROR: TTL file not found: {ttl_path}", file=sys.stderr)
        sys.exit(1)
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {ttl_path} ...")
    g = Graph()
    g.parse(str(ttl_path), format="turtle")

    # Find the ConceptScheme
    schemes = list(g.subjects(RDF.type, SKOS.ConceptScheme))
    if not schemes:
        print("ERROR: No skos:ConceptScheme found in the TTL file.", file=sys.stderr)
        sys.exit(1)
    if len(schemes) > 1:
        print(f"WARNING: Multiple ConceptSchemes found, using first: {schemes[0]}")
    scheme_uri = schemes[0]
    print(f"Found ConceptScheme: {scheme_uri}")

    metadata_html = build_metadata_html(g, scheme_uri)

    html = html_path.read_text(encoding="utf-8")
    updated = inject(html, metadata_html)

    out_path.write_text(updated, encoding="utf-8")
    print(f"Done. Written to {out_path}")


if __name__ == "__main__":
    main()
