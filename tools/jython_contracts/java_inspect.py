"""Inspect Java classes for Jython contract authoring help."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from . import JAVA_ROOT, PROJECT_ROOT
from .registry import fqcn_to_java_path, java_path_to_fqcn


@dataclass
class MethodInfo:
    signature: str
    javadoc: str = ""


@dataclass
class ClassInfo:
    fqcn: str
    path: Path
    kind: str  # class | interface | enum
    javadoc: str = ""
    methods: List[MethodInfo] = field(default_factory=list)
    constructors: List[MethodInfo] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    usages: List[Tuple[str, int, str]] = field(default_factory=list)
    binding_hint: Optional[str] = None


def _strip_javadoc(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        line = re.sub(r"^\s*/?\*+/?\s?", "", line)
        lines.append(line.rstrip())
    # Trim leading/trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def _find_java_file(fqcn_or_name: str) -> Path:
    """Resolve FQCN or simple class name to a .java path."""
    if "." in fqcn_or_name:
        path = fqcn_to_java_path(fqcn_or_name)
        if path and path.exists():
            return path
        raise FileNotFoundError(f"Java source not found for {fqcn_or_name}")

    matches = list(JAVA_ROOT.rglob(f"{fqcn_or_name}.java"))
    if not matches:
        raise FileNotFoundError(f"No Java file named {fqcn_or_name}.java under org/uacalc")
    if len(matches) > 1:
        # Prefer exact unique if same name in different packages — return first sorted, note later
        matches = sorted(matches)
    return matches[0]


def parse_java_class(path: Path) -> ClassInfo:
    text = path.read_text(encoding="utf-8", errors="replace")
    fqcn = java_path_to_fqcn(path)
    simple = path.stem

    kind_match = re.search(
        rf"^\s*public\s+(?:abstract\s+|final\s+)*(class|interface|enum)\s+{re.escape(simple)}\b",
        text,
        re.MULTILINE,
    )
    kind = kind_match.group(1) if kind_match else "class"

    # Class-level javadoc: comment immediately before the public type declaration
    class_javadoc = ""
    if kind_match:
        before = text[: kind_match.start()]
        doc_match = re.search(r"/\*\*(.*?)\*/\s*$", before, re.DOTALL)
        if doc_match:
            class_javadoc = _strip_javadoc(doc_match.group(0))

    methods: List[MethodInfo] = []
    constructors: List[MethodInfo] = []
    fields: List[str] = []

    # Public methods / constructors with optional preceding javadoc
    member_pat = re.compile(
        r"(?:/\*\*(.*?)\*/\s*)?"
        r"public\s+"
        r"(?:static\s+|final\s+|synchronized\s+|native\s+|abstract\s+|default\s+)*"
        r"(?:<[^>]+>\s*)?"
        r"(?:([\w.<>,\[\]\s]+?)\s+)?"
        r"(\w+)\s*"
        r"\(([^;{]*)\)"
        r"(?:\s*throws\s+[^{;]+)?\s*"
        r"[{;]",
        re.DOTALL,
    )

    for m in member_pat.finditer(text):
        doc_raw, return_type, name, params = m.group(1), m.group(2), m.group(3), m.group(4)
        # Skip if this matched the class/interface/enum declaration itself
        if name in ("class", "interface", "enum", "if", "for", "while", "switch", "catch"):
            continue
        params_clean = " ".join(params.split())
        javadoc = _strip_javadoc(f"/**{doc_raw}*/") if doc_raw else ""
        if name == simple:
            sig = f"public {name}({params_clean})"
            constructors.append(MethodInfo(signature=sig, javadoc=javadoc))
        else:
            ret = (return_type or "").strip()
            # Filter out field-like false positives where "return type" looks wrong
            if not ret and name != simple:
                continue
            sig = f"public {ret} {name}({params_clean})".strip()
            methods.append(MethodInfo(signature=sig, javadoc=javadoc))

    field_pat = re.compile(
        r"^\s*public\s+(?:static\s+|final\s+)*([\w.<>,\[\]]+)\s+(\w+)\s*(?:=|;)",
        re.MULTILINE,
    )
    for m in field_pat.finditer(text):
        fields.append(f"public {m.group(1)} {m.group(2)}")

    return ClassInfo(
        fqcn=fqcn,
        path=path,
        kind=kind,
        javadoc=class_javadoc,
        methods=methods,
        constructors=constructors,
        fields=fields,
    )


def find_usages(
    simple_name: str,
    fqcn: str,
    *,
    max_hits: int = 15,
    context_lines: int = 0,
) -> List[Tuple[str, int, str]]:
    """
    Find usage examples across the codebase.
    Returns list of (rel_path, line_number, line_text).
    """
    search_roots = [
        PROJECT_ROOT / "org" / "uacalc" / "example",
        PROJECT_ROOT / "python" / "uacalc" / "examples",
        PROJECT_ROOT / "jython_comparison",
        PROJECT_ROOT / "org" / "uacalc",
    ]
    patterns = [
        re.compile(rf"\b{re.escape(simple_name)}\b"),
        re.compile(rf"\b{re.escape(fqcn)}\b"),
        re.compile(rf"from org\.uacalc\.\w+ import.*\b{re.escape(simple_name)}\b"),
        re.compile(rf"import\s+{re.escape(fqcn)}\b"),
    ]
    exts = {".java", ".py", ".md"}
    hits: List[Tuple[str, int, str]] = []
    seen = set()

    for root in search_roots:
        if not root.exists():
            continue
        files = [root] if root.is_file() else root.rglob("*")
        for path in files:
            if not path.is_file() or path.suffix not in exts:
                continue
            # Skip the defining file itself for "usage"
            try:
                rel = str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
            except ValueError:
                rel = str(path)
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, start=1):
                if not any(p.search(line) for p in patterns):
                    continue
                # Prefer example / comparison dirs; still allow general org hits
                key = (rel, i)
                if key in seen:
                    continue
                seen.add(key)
                # Skip package/import-only noise in defining source later
                hits.append((rel, i, line.strip()))
                if len(hits) >= max_hits * 3:
                    break
            if len(hits) >= max_hits * 3:
                break

    # Rank: example/jython_comparison first, then others; skip defining file decls
    def rank(item: Tuple[str, int, str]) -> Tuple[int, str, int]:
        rel, line_no, _ = item
        if "example" in rel or "jython_comparison" in rel:
            pri = 0
        elif rel.startswith("python/"):
            pri = 1
        else:
            pri = 2
        return (pri, rel, line_no)

    hits.sort(key=rank)
    # Filter out the class declaration line in its own file
    defining = fqcn.replace(".", "/") + ".java"
    filtered = []
    for rel, line_no, text in hits:
        if rel.endswith(defining) and re.search(rf"\b(class|interface|enum)\s+{simple_name}\b", text):
            continue
        filtered.append((rel, line_no, text))
        if len(filtered) >= max_hits:
            break
    return filtered


def binding_presence(simple_name: str) -> Optional[str]:
    """Hint whether the type appears in type stubs or Rust bindings."""
    stub = PROJECT_ROOT / "python" / "uacalc_lib" / "__init__.pyi"
    hints = []
    if stub.exists():
        text = stub.read_text(encoding="utf-8", errors="replace")
        if re.search(rf"\bclass {re.escape(simple_name)}\b", text) or re.search(
            rf"\b{re.escape(simple_name)}\b", text
        ):
            hints.append("mentioned in python/uacalc_lib/__init__.pyi")
    rust_src = PROJECT_ROOT / "uacalc_lib" / "src"
    if rust_src.exists():
        for rs in rust_src.rglob("*.rs"):
            content = rs.read_text(encoding="utf-8", errors="replace")
            if f'm.add("{simple_name}"' in content or f"struct {simple_name}" in content:
                try:
                    rel = str(rs.resolve().relative_to(PROJECT_ROOT.resolve()))
                except ValueError:
                    rel = str(rs)
                hints.append(f"bound/registered in {rel}")
                break
    return "; ".join(hints) if hints else "not found in type stubs / uacalc_lib registrations"


def inspect_class(fqcn_or_name: str, max_usages: int = 15) -> ClassInfo:
    path = _find_java_file(fqcn_or_name)
    info = parse_java_class(path)
    info.usages = find_usages(path.stem, info.fqcn, max_hits=max_usages)
    info.binding_hint = binding_presence(path.stem)
    return info


def format_inspection(info: ClassInfo) -> str:
    lines = [
        f"Class: {info.fqcn}",
        f"Kind:  {info.kind}",
        f"File:  {info.path.resolve().relative_to(PROJECT_ROOT.resolve())}",
        "",
        "Documentation:",
    ]
    if info.javadoc:
        for doc_line in info.javadoc.splitlines():
            lines.append(f"  {doc_line}")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append("Constructors:")
    if info.constructors:
        for c in info.constructors[:30]:
            lines.append(f"  {c.signature}")
    else:
        lines.append("  (none found)")

    lines.append("")
    lines.append("Public methods:")
    if info.methods:
        for m in info.methods[:60]:
            lines.append(f"  {m.signature}")
            if m.javadoc:
                first = m.javadoc.splitlines()[0]
                lines.append(f"    # {first}")
    else:
        lines.append("  (none found)")

    if info.fields:
        lines.append("")
        lines.append("Public fields:")
        for f in info.fields[:40]:
            lines.append(f"  {f}")

    lines.append("")
    lines.append("Binding hint:")
    lines.append(f"  {info.binding_hint or '(unknown)'}")

    lines.append("")
    lines.append("Usage examples:")
    if info.usages:
        for rel, line_no, text in info.usages:
            lines.append(f"  {rel}:{line_no}: {text}")
    else:
        lines.append("  (none found)")

    return "\n".join(lines) + "\n"
