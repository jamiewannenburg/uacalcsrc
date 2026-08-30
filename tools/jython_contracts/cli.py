"""Command-line interface for Jython compatibility contracts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import CONTRACTS_DIR, DEFAULT_EXCLUDE_PACKAGES, PROJECT_ROOT, VALID_STATUSES
from .java_inspect import format_inspection, inspect_class
from .registry import (
    discover_java_types,
    effective_contract,
    effective_status,
    format_contract,
    init_contract,
    load_all_contracts,
    set_status,
)
from .validate import format_issues, validate_contracts
from .coverage import build_coverage, format_coverage


def _contracts_dir(args: argparse.Namespace) -> Path:
    return Path(args.contracts_dir) if getattr(args, "contracts_dir", None) else CONTRACTS_DIR


def cmd_status(args: argparse.Namespace) -> int:
    contracts_dir = _contracts_dir(args)
    contracts = load_all_contracts(contracts_dir)
    exclude = set(DEFAULT_EXCLUDE_PACKAGES)
    if args.include_ui:
        exclude.discard("ui")
        exclude.discard("nbui")

    types = discover_java_types(exclude_packages=exclude)
    status_filter: Optional[set] = set(args.status) if args.status else None

    rows = []
    for fqcn, path in types:
        status = effective_status(fqcn, contracts=contracts, contracts_dir=contracts_dir)
        if status_filter and status not in status_filter:
            continue
        has_file = fqcn in contracts
        pkg = fqcn.rsplit(".", 1)[0]
        has_pkg = pkg in contracts
        marker = []
        if has_file:
            marker.append("file")
        if has_pkg:
            marker.append("pkg")
        scope = ",".join(marker) if marker else "-"
        try:
            rel = str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
        except ValueError:
            rel = str(path)
        rows.append((status, fqcn, scope, rel))

    # Also show package-only contracts that aren't types
    for target, contract in sorted(contracts.items()):
        if contract.level != "package":
            continue
        if status_filter and contract.status not in status_filter:
            continue
        # Skip if already shown via types listing interest — show package contracts in a section
        pass

    width = max((len(r[1]) for r in rows), default=10)
    print(f"{'STATUS':<12} {'TARGET':<{width}}  CONTRACT  SOURCE")
    print(f"{'-'*12} {'-'*width}  --------  ------")
    counts = {"pending": 0, "implemented": 0, "ignored": 0}
    for status, fqcn, scope, rel in rows:
        counts[status] = counts.get(status, 0) + 1
        print(f"{status:<12} {fqcn:<{width}}  {scope:<8}  {rel}")

    print()
    print(
        f"Total: {len(rows)}  "
        f"implemented={counts.get('implemented', 0)}  "
        f"pending={counts.get('pending', 0)}  "
        f"ignored={counts.get('ignored', 0)}"
    )

    if args.packages:
        print()
        print("Package contracts:")
        for target, contract in sorted(contracts.items()):
            if contract.level == "package":
                print(f"  {contract.status:<12} {target}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    contracts_dir = _contracts_dir(args)
    try:
        contract = init_contract(
            args.target,
            level=args.level,
            status=args.status or "pending",
            contracts_dir=contracts_dir,
            force=args.force,
        )
    except FileExistsError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"Created {contract.path}")
    print(format_contract(contract), end="")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    contracts_dir = _contracts_dir(args)
    try:
        contract = set_status(
            args.target,
            args.status,
            reason=args.reason,
            contracts_dir=contracts_dir,
        )
    except (ValueError, FileExistsError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"Updated {contract.path}")
    print(f"  status: {contract.status}")
    if contract.ignore_reason:
        print(f"  ignore_reason: {contract.ignore_reason}")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    try:
        info = inspect_class(args.cls, max_usages=args.max_usages)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(format_inspection(info), end="")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    contracts_dir = _contracts_dir(args)
    contracts = load_all_contracts(contracts_dir)
    eff = effective_contract(args.target, contracts=contracts, contracts_dir=contracts_dir)
    if eff is None:
        print(f"No contract found for {args.target} (effective status: pending)")
        return 1
    print(f"# Effective contract for {args.target}")
    print(f"# (merged most-general → most-refined; refined wins)")
    print(format_contract(eff), end="")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    contracts_dir = _contracts_dir(args)
    issues = validate_contracts(contracts_dir)
    print(format_issues(issues), end="")
    errors = sum(1 for i in issues if i.severity == "error")
    return 1 if errors else 0


def cmd_coverage(args: argparse.Namespace) -> int:
    contracts_dir = _contracts_dir(args)
    report = build_coverage(contracts_dir)
    print(format_coverage(report, verbose=args.verbose), end="")
    if report.missing_script_files:
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jython_contracts",
        description="Manage hierarchical Jython compatibility contracts for UACalc.",
    )
    parser.add_argument(
        "--contracts-dir",
        default=str(CONTRACTS_DIR),
        help=f"Directory of contract YAML files (default: {CONTRACTS_DIR})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="List Java types with effective contract status")
    p_status.add_argument(
        "--status",
        nargs="+",
        choices=sorted(VALID_STATUSES),
        help="Only show these statuses",
    )
    p_status.add_argument(
        "--include-ui",
        action="store_true",
        help="Include org.uacalc.ui and org.uacalc.nbui",
    )
    p_status.add_argument(
        "--packages",
        action="store_true",
        help="Also list package-level contracts",
    )
    p_status.set_defaults(func=cmd_status)

    p_init = sub.add_parser("init", help="Scaffold a package or file contract YAML")
    p_init.add_argument("target", help="FQCN or package, e.g. org.uacalc.alg.BasicAlgebra")
    p_init.add_argument("--level", choices=["package", "file"], help="Override inferred level")
    p_init.add_argument("--status", choices=sorted(VALID_STATUSES), default="pending")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing contract")
    p_init.set_defaults(func=cmd_init)

    p_set = sub.add_parser("set-status", help="Update contract status")
    p_set.add_argument("target", help="FQCN or package")
    p_set.add_argument("status", choices=sorted(VALID_STATUSES))
    p_set.add_argument("--reason", help="Required when status is ignored")
    p_set.set_defaults(func=cmd_set_status)

    p_inspect = sub.add_parser(
        "inspect",
        help="Show location, docs, public API, and usage examples for a Java class",
    )
    p_inspect.add_argument("cls", help="FQCN or simple class name")
    p_inspect.add_argument("--max-usages", type=int, default=15)
    p_inspect.set_defaults(func=cmd_inspect)

    p_show = sub.add_parser("show", help="Print effective merged contract for a target")
    p_show.add_argument("target", help="FQCN or package")
    p_show.set_defaults(func=cmd_show)

    p_val = sub.add_parser("validate", help="Validate contracts against python/org shims")
    p_val.set_defaults(func=cmd_validate)

    p_cov = sub.add_parser(
        "coverage",
        help="Show which declared surface symbols are covered by parity scripts",
    )
    p_cov.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="List each surface symbol and coverage mark",
    )
    p_cov.set_defaults(func=cmd_coverage)

    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
