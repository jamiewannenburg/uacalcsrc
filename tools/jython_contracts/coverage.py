"""Coverage of declared contract surface by parity scripts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from . import PROJECT_ROOT
from .registry import (
    collect_script_entries,
    load_all_contracts,
    normalize_testing,
    surface_symbols,
)


@dataclass
class CoverageReport:
    """Which surface symbols are covered by testing.scripts covers lists."""

    by_contract: Dict[str, Dict[str, object]] = field(default_factory=dict)
    all_declared: Set[str] = field(default_factory=set)
    all_covered: Set[str] = field(default_factory=set)
    scripts: List[Dict] = field(default_factory=list)
    missing_script_files: List[str] = field(default_factory=list)


def build_coverage(
    contracts_dir: Optional[Path] = None,
) -> CoverageReport:
    contracts = (
        load_all_contracts(contracts_dir) if contracts_dir else load_all_contracts()
    )
    report = CoverageReport()
    report.scripts = collect_script_entries(contracts)

    for script in report.scripts:
        path = PROJECT_ROOT / script["path"]
        if not path.is_file():
            report.missing_script_files.append(script["path"])

    for target, contract in sorted(contracts.items()):
        if contract.status == "ignored":
            continue
        declared = surface_symbols(contract.surface)
        testing = normalize_testing(contract.testing)
        covered: Set[str] = set()
        for script in testing["scripts"]:
            covered.update(script["covers"])

        missing = [s for s in declared if s not in covered]
        report.by_contract[target] = {
            "status": contract.status,
            "declared": declared,
            "covered": sorted(covered),
            "missing": missing,
            "has_notes": bool(testing["notes"].strip()),
            "script_count": len(testing["scripts"]),
        }
        report.all_declared.update(declared)
        report.all_covered.update(covered & set(declared))

    return report


def format_coverage(report: CoverageReport, *, verbose: bool = False) -> str:
    lines: List[str] = []
    lines.append("Parity script coverage of declared contract surface")
    lines.append("(covers lists on testing.scripts vs surface aliases/statics/str_parity)")
    lines.append("")

    uncovered_contracts = []
    for target, info in report.by_contract.items():
        declared = info["declared"]
        missing = info["missing"]
        if not declared and not info["script_count"]:
            continue
        status = "OK" if declared and not missing else ("partial" if declared else "no-surface")
        if missing or (declared and not info["covered"]):
            uncovered_contracts.append(target)
        lines.append(
            f"{status:<8} {target}  "
            f"declared={len(declared)} covered={len(declared) - len(missing)} "
            f"scripts={info['script_count']} notes={'yes' if info['has_notes'] else 'no'}"
        )
        if verbose and declared:
            for sym in declared:
                mark = "x" if sym not in missing else " "
                lines.append(f"         [{mark}] {sym}")
            if info["covered"]:
                extra = [c for c in info["covered"] if c not in declared]
                for sym in extra:
                    lines.append(f"         [+] {sym}  (covered but not on this surface)")

    lines.append("")
    declared_n = len(report.all_declared)
    covered_n = len(report.all_covered)
    lines.append(
        f"Surface symbols: {covered_n}/{declared_n} covered by at least one script"
    )
    lines.append(f"Parity scripts referenced: {len(report.scripts)}")
    if report.missing_script_files:
        lines.append("Missing script files:")
        for path in report.missing_script_files:
            lines.append(f"  - {path}")
    if uncovered_contracts:
        lines.append(
            f"Contracts with uncovered surface symbols: {len(uncovered_contracts)}"
        )
    return "\n".join(lines) + "\n"
