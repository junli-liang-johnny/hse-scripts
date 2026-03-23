#!/usr/bin/env python3
"""
hse-pipeline: CLI tool for running and inspecting HSE data pipeline outputs.

Subcommands:
    run <version>         Run the pipeline shell script for a given version
    check <version>       Check RDF stats, DQ reports, and data integrity
    compare <vA> <vB>     Compare DQ outputs between two pipeline versions
"""
import argparse
import csv
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

# hse-scripts/ is the parent of the scripts/ package directory
SCRIPTS_ROOT = Path(__file__).parent.parent
# hse-data/ sits next to hse-scripts/
DATA_ROOT = SCRIPTS_ROOT.parent / "hse-data"


def mapping_dir(version: str) -> Path:
    return DATA_ROOT / "mapping" / version


def dq_dir(version: str) -> Path:
    return DATA_ROOT / "output" / "dq" / version


def shell_script(version: str) -> Path:
    return SCRIPTS_ROOT / f"main.{version}.sh"


# ---------------------------------------------------------------------------
# Terminal helpers
# ---------------------------------------------------------------------------

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


def _ok(msg: str) -> None:
    print(f"  {_GREEN}✓{_RESET} {msg}")


def _fail(msg: str) -> None:
    print(f"  {_RED}✗{_RESET} {msg}")


def _warn(msg: str) -> None:
    print(f"  {_YELLOW}⚠{_RESET} {msg}")


def _header(msg: str) -> None:
    print()
    print("=" * 60)
    print(msg)
    print("=" * 60)


def _section(msg: str) -> None:
    print()
    print(f"── {msg}")
    print("─" * 60)


def _load_csv(path: Path) -> list[dict] | None:
    if not path.exists():
        return None
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _norm_id(uri: str) -> str | None:
    """Extract hseNNNNNNNN from any URI form."""
    m = re.search(r"(hse\d+)$", uri)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def cmd_run(args):
    script = shell_script(args.version)
    if not script.exists():
        print(f"✗ Script not found: {script}", file=sys.stderr)
        print(f"  Available scripts:", file=sys.stderr)
        for s in sorted(SCRIPTS_ROOT.glob("main.v*.sh")):
            print(f"    {s.name}", file=sys.stderr)
        sys.exit(1)
    print(f"Running {script.name} (cwd: {SCRIPTS_ROOT}) ...")
    result = subprocess.run(["bash", str(script)], cwd=str(SCRIPTS_ROOT))
    sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# check — RDF statistics
# ---------------------------------------------------------------------------

def _check_rdf(version: str) -> None:
    _section("RDF Statistics")
    try:
        from rdflib import Graph, Namespace
    except ImportError:
        _fail("rdflib not installed — skipping RDF stats")
        return

    mappings = mapping_dir(version) / "mappings_final.ttl"
    pht = DATA_ROOT / "mapping" / "terminology" / "terms-1.0.1.ttl"

    if not mappings.exists():
        _fail(f"mappings_final.ttl not found: {mappings}")
        return

    print(f"  Loading {mappings.name} ...", end=" ", flush=True)
    g = Graph()
    g.parse(mappings, format="turtle")
    size_kb = mappings.stat().st_size / 1024
    print(f"{len(g):,} triples  ({size_kb:.1f} KB)")

    total = len(g)
    if pht.exists():
        g2 = Graph()
        g2.parse(pht, format="turtle")
        print(f"  Loading pht.ttl ...          {len(g2):,} triples")
        total += len(g2)
    else:
        _warn(f"pht.ttl not found: {pht}")

    print(f"\n  Total triples: {total:,}")

    RDF_TYPE = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#").type
    type_counts: Counter = Counter()
    for _, _, o in g.triples((None, RDF_TYPE, None)):
        s = str(o)
        name = s.split("#")[-1] if "#" in s else s.split("/")[-1]
        type_counts[name] += 1

    print("\n  Entity counts:")
    for name, count in type_counts.most_common(15):
        print(f"    {name:35s} {count:6,}")


# ---------------------------------------------------------------------------
# check — DQ report statistics
# ---------------------------------------------------------------------------

def _check_dq(version: str) -> None:
    _section("DQ Report Statistics")
    dq = dq_dir(version)

    # Completeness
    comp_path = dq / "mro_fields_completeness.csv"
    comp = _load_csv(comp_path)
    if comp is None:
        _fail(f"mro_fields_completeness.csv not found: {comp_path}")
    else:
        print(f"\n  Completeness ({comp_path.name}): {len(comp)} indicators")
        scores = []
        for r in comp:
            raw = r.get("overallCompletenessPercent", "")
            try:
                scores.append(float(raw.replace("%", "")))
            except (ValueError, AttributeError):
                pass
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  Average overall completeness: {avg:.1f}%")
            dist: Counter = Counter()
            for s in scores:
                lo = int(s // 10) * 10
                dist[f"{lo}-{lo + 9}%"] += 1
            print("  Score distribution:")
            for bucket in sorted(dist):
                bar = "█" * (dist[bucket] // 2)
                print(f"    {bucket:8s}  {dist[bucket]:4d}  {bar}")

    # Feasibility
    feas_path = dq / "feasibility_test.csv"
    feas = _load_csv(feas_path)
    if feas is None:
        _fail(f"feasibility_test.csv not found: {feas_path}")
    else:
        print(f"\n  Feasibility ({feas_path.name}): {len(feas)} indicators")
        total = len(feas)
        pass_dist: Counter = Counter(r.get("pass", "") for r in feas)
        for val, cnt in sorted(pass_dist.items(), key=lambda x: -x[1]):
            pct = cnt / total * 100
            print(f"    pass={val:<10s} {cnt:4d}  ({pct:.1f}%)")
        score_dist: Counter = Counter(r.get("dq_score", "") for r in feas)
        print("  DQ score distribution:")
        for val, cnt in sorted(score_dist.items()):
            print(f"    score={val}  {cnt:4d}")


# ---------------------------------------------------------------------------
# check — data integrity
# ---------------------------------------------------------------------------

def _check_integrity(version: str) -> None:
    _section("Data Integrity Checks")
    dq = dq_dir(version)

    # 1. Indicator URI well-formedness
    comp = _load_csv(dq / "mro_fields_completeness.csv")
    if comp is not None:
        expected_prefix = "https://w3id.org/hse/indicator/"
        bad = [r["indicator"] for r in comp if not r["indicator"].startswith(expected_prefix)]
        ghost = [r["indicator"] for r in comp if r["indicator"] == "https://w3id.org/hse/indicator"]
        if bad:
            _fail(f"Malformed indicator URIs (missing slash / wrong base): {len(bad)}/{len(comp)}")
            for uri in bad[:5]:
                print(f"      {uri}")
            if len(bad) > 5:
                print(f"      ... and {len(bad) - 5} more")
        else:
            _ok(f"All {len(comp)} indicator URIs are well-formed")

        if ghost:
            _fail(f"Ghost rows (bare namespace URI with no ID): {len(ghost)}")
        else:
            _ok("No ghost/empty indicator rows")

    # 2. memberOfGroup URI domain consistency
    members_path = mapping_dir(version) / "indicator_group_members.csv"
    members = _load_csv(members_path)
    if members is not None:
        old_domain = [r for r in members if "hse.ie" in r.get("member_id", "")]
        if old_domain:
            _fail(
                f"indicator_group_members.csv: {len(old_domain)} member URIs use old "
                f"'hse.ie' domain instead of 'w3id.org/hse/indicator/...'"
            )
            for r in old_domain[:3]:
                print(f"      {r['member_id']}")
        else:
            _ok("All group member URIs use the correct domain")
    else:
        _warn(f"indicator_group_members.csv not found: {members_path}")

    # 3. Row-count consistency between reports
    feas = _load_csv(dq / "feasibility_test.csv")
    if comp is not None and feas is not None:
        delta = abs(len(comp) - len(feas))
        if delta == 0:
            _ok("Completeness and feasibility row counts match")
        elif delta == 1:
            _warn(
                f"Completeness ({len(comp)}) and feasibility ({len(feas)}) differ by 1 row "
                f"(likely a ghost row)"
            )
        else:
            _fail(
                f"Completeness ({len(comp)}) and feasibility ({len(feas)}) "
                f"differ by {delta} rows"
            )


def cmd_check(args):
    _header(f"Pipeline Check — {args.version}")
    _check_rdf(args.version)
    _check_dq(args.version)
    _check_integrity(args.version)
    print()


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

def cmd_compare(args):
    vA, vB = args.version_a, args.version_b
    _header(f"Pipeline Compare — {vA}  vs  {vB}")

    def load_by_id(path: Path) -> dict | None:
        rows = _load_csv(path)
        if rows is None:
            return None
        return {
            _norm_id(r.get("indicator", "")): r
            for r in rows
            if _norm_id(r.get("indicator", ""))
        }

    # --- Completeness comparison ---
    _section("Completeness")
    ca = load_by_id(dq_dir(vA) / "mro_fields_completeness.csv")
    cb = load_by_id(dq_dir(vB) / "mro_fields_completeness.csv")

    if ca is None:
        _fail(f"mro_fields_completeness.csv not found for {vA}")
    elif cb is None:
        _fail(f"mro_fields_completeness.csv not found for {vB}")
    else:
        only_a = set(ca) - set(cb)
        only_b = set(cb) - set(ca)
        both = set(ca) & set(cb)

        print(f"\n  {vA}: {len(ca)} indicators  |  {vB}: {len(cb)} indicators")
        print(f"  Shared:        {len(both)}")
        print(f"  Only in {vA}:  {len(only_a)}")
        print(f"  Only in {vB}:  {len(only_b)}")

        def score(r: dict) -> float:
            try:
                return float(r.get("overallCompletenessPercent", "0").replace("%", ""))
            except ValueError:
                return 0.0

        improved, worsened, unchanged = [], [], []
        for hid in sorted(both):
            sa, sb = score(ca[hid]), score(cb[hid])
            d = sb - sa
            if d > 0:
                improved.append((hid, sa, sb, d))
            elif d < 0:
                worsened.append((hid, sa, sb, d))
            else:
                unchanged.append(hid)

        print(f"\n  Score changes across {len(both)} shared indicators:")
        print(f"    Improved:  {len(improved)}")
        print(f"    Worsened:  {len(worsened)}")
        print(f"    Unchanged: {len(unchanged)}")

        if improved:
            print(f"\n  Top 5 improved ({vA} → {vB}):")
            for hid, sa, sb, d in sorted(improved, key=lambda x: -x[3])[:5]:
                print(f"    {hid}  {sa:.0f}% → {sb:.0f}%  ({d:+.0f}pp)")
        if worsened:
            print(f"\n  Top 5 worsened ({vA} → {vB}):")
            for hid, sa, sb, d in sorted(worsened, key=lambda x: x[3])[:5]:
                print(f"    {hid}  {sa:.0f}% → {sb:.0f}%  ({d:+.0f}pp)")

    # --- Feasibility comparison ---
    _section("Feasibility")
    fa = load_by_id(dq_dir(vA) / "feasibility_test.csv")
    fb = load_by_id(dq_dir(vB) / "feasibility_test.csv")

    if fa is None:
        _fail(f"feasibility_test.csv not found for {vA}")
    elif fb is None:
        _fail(f"feasibility_test.csv not found for {vB}")
    else:
        only_a = set(fa) - set(fb)
        only_b = set(fb) - set(fa)
        both = set(fa) & set(fb)

        print(f"\n  {vA}: {len(fa)} indicators  |  {vB}: {len(fb)} indicators")
        print(f"  Shared:        {len(both)}")
        print(f"  Only in {vA}:  {len(only_a)}")
        print(f"  Only in {vB}:  {len(only_b)}")

        regressions, promotions, other = [], [], []
        for hid in sorted(both):
            pa = fa[hid].get("pass", "")
            pb = fb[hid].get("pass", "")
            if pa == pb:
                continue
            if pa == "true" and pb != "true":
                regressions.append((hid, pa, pb))
            elif pb == "true" and pa != "true":
                promotions.append((hid, pa, pb))
            else:
                other.append((hid, pa, pb))

        print(f"\n  Pass-status changes across {len(both)} shared indicators:")
        if regressions:
            _fail(f"Regressions (was passing, now not): {len(regressions)}")
            for hid, pa, pb in regressions[:10]:
                print(f"      {hid}  {pa} → {pb}")
        else:
            _ok("No regressions")

        if promotions:
            _ok(f"Promotions (now passing): {len(promotions)}")
            for hid, pa, pb in promotions[:10]:
                print(f"      {hid}  {pa} → {pb}")

        if other:
            print(f"  Other changes: {len(other)}")
            for hid, pa, pb in other[:5]:
                print(f"      {hid}  {pa} → {pb}")

        # Detailed diff for regressions
        if regressions:
            print(f"\n  Regression details:")
            for hid, _, _ in regressions[:5]:
                ra, rb = fa[hid], fb[hid]
                print(f"\n    {hid}:")
                skip = {"indicator", "indicatorTitle"}
                for col in ra:
                    if col in rb and ra[col] != rb[col] and col not in skip:
                        print(f"      {col}:")
                        print(f"        {vA}: {ra[col][:90]}")
                        print(f"        {vB}: {rb[col][:90]}")

    print()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="hse-pipeline",
        description="HSE data pipeline runner and output inspector",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    # run
    p_run = sub.add_parser("run", help="Run the pipeline shell script for a given version")
    p_run.add_argument("version", help="Pipeline version, e.g. v10")
    p_run.set_defaults(func=cmd_run)

    # check
    p_check = sub.add_parser(
        "check", help="Check RDF stats, DQ reports, and data integrity for a version"
    )
    p_check.add_argument("version", help="Pipeline version, e.g. v10")
    p_check.set_defaults(func=cmd_check)

    # compare
    p_compare = sub.add_parser(
        "compare", help="Compare DQ outputs between two pipeline versions"
    )
    p_compare.add_argument("version_a", help="Baseline version, e.g. v9")
    p_compare.add_argument("version_b", help="New version, e.g. v10")
    p_compare.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
