"""Scan Java sources for the public Jython-facing API surface.

The previous line-oriented ``public ... name(`` heuristic counted several
things that are not library surface: anonymous inner-class Operation methods,
members that only exist inside comments, GUI types, ``main`` demo helpers,
package-private members, and legacy ``_old`` / ``XX`` overloads.

This scanner categorises every excluded member with an explicit reason so
coverage and inventory reports can show wrapped / tested / unwrapped /
excluded-by-category instead of silently dropping names.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from . import JAVA_ROOT, PROJECT_ROOT


# Categories shown in coverage / inventory reports. Keep names stable.
ANONYMOUS_INNER_CLASS = "anonymous_inner_class"
COMMENTED_OUT = "commented_out"
GUI = "gui"
MAIN = "main"
PACKAGE_PRIVATE = "package_private"
PROTECTED = "protected"
NON_PUBLIC_TYPE = "non_public_type"
LEGACY = "legacy"

EXCLUSION_CATEGORIES = (
    ANONYMOUS_INNER_CLASS,
    COMMENTED_OUT,
    GUI,
    MAIN,
    PACKAGE_PRIVATE,
    PROTECTED,
    NON_PUBLIC_TYPE,
    LEGACY,
)

CATEGORY_REASONS = {
    ANONYMOUS_INNER_CLASS: (
        "method of an anonymous inner class (typically an Operation), "
        "not a member of the enclosing type"
    ),
    COMMENTED_OUT: "declared only inside a comment; not part of the live class",
    GUI: (
        "GUI/Swing widget class (org.uacalc.ui, org.uacalc.nbui, FrameShower, "
        "or a JFrame/JPanel/JDialog subclass); out of Jython library scope"
    ),
    MAIN: "Java main() / demo main; development helper, not library surface",
    PACKAGE_PRIVATE: "package-private; not public API",
    PROTECTED: "protected; not public API",
    NON_PUBLIC_TYPE: "member of a non-public nested type",
    LEGACY: "legacy public overload (name ends in _old or XX); not current surface",
}

_KEYWORDS = frozenset(
    {
        "if",
        "for",
        "while",
        "switch",
        "return",
        "throw",
        "new",
        "true",
        "false",
        "null",
        "class",
        "interface",
        "enum",
        "catch",
        "try",
        "else",
        "do",
        "case",
        "break",
        "continue",
        "synchronized",
        "assert",
        "package",
        "import",
        "public",
        "private",
        "protected",
        "static",
        "final",
        "void",
        "abstract",
        "default",
        "native",
        "strictfp",
        "extends",
        "implements",
        "throws",
        "this",
        "super",
    }
)

_TYPE_DECL_RE = re.compile(
    r"(?:(?P<vis>public|protected|private)\s+)?"
    r"(?:(?:static|final|abstract|strictfp)\s+)*"
    r"(?P<kind>class|interface|enum)\s+(?P<name>\w+)",
)

_MEMBER_RE = re.compile(
    r"^[ \t]*(?:(?P<vis>public|protected|private)\s+)?"
    r"(?P<mods>(?:static|final|synchronized|native|abstract|default|strictfp)\s+)*"
    r"(?:<[^;{}\n]+?>\s*)?"
    r"(?:(?P<ret>[\w.<>,\[\]][\w.<>,\[\]\s]*?)\s+)?"
    r"(?P<name>\w+)\s*"
    r"\((?P<params>[^;{}]*)\)"
    r"(?:\s*throws\s+[^{;]+)?"
    r"\s*[{;]",
    re.MULTILINE | re.DOTALL,
)

_BAD_RET_RE = re.compile(
    r"\b(return|new|throw|if|for|while|switch|catch|class|interface|enum|package|import)\b"
)

_COMMENTED_PUBLIC_RE = re.compile(
    r"public\s+(?:static\s+|final\s+|synchronized\s+|native\s+|abstract\s+|default\s+)*"
    r"(?:<[^;()]+?>\s*)?"
    r"(?:([\w.<>,\[\]]+(?:\s*<[^;()]+?>)?(?:\[\])*)\s+)?"
    r"(\w+)\s*\([^;{}]*\)",
    re.DOTALL,
)

_PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)

# Suffixes of leftover public overloads: sgClose_old, Cg_Old, sgCloseXX.
# Bare "...Old" (increasingSequenceIncrementorOld) is still live wrapped API.
_LEGACY_NAME_RE = re.compile(r"(?:_old|XX)$", re.IGNORECASE)

_GUI_SUPERTYPES = frozenset(
    {
        "JFrame",
        "JPanel",
        "JDialog",
        "JWindow",
        "JComponent",
        "JApplet",
        "JInternalFrame",
        "JFileChooser",
        "SwingWorker",
    }
)

_GUI_TYPE_NAMES = frozenset({"FrameShower", "LatDrawer", "LatDrawPanel", "UACalculator"})

_SKIP_MEMBER_NAMES = frozenset(_KEYWORDS)


@dataclass
class JavaMember:
    """One constructor or method found in a Java compilation unit."""

    name: str
    kind: str  # method | constructor
    enclosing_type: str
    visibility: str  # public | protected | private | package
    exclusion: Optional[str]
    line: int
    signature: str
    is_static: bool = False


@dataclass
class JavaTypeSurface:
    fqcn: str
    simple_name: str
    kind: str
    visibility: str
    package: str
    source_relpath: str
    is_gui: bool
    members: List[JavaMember] = field(default_factory=list)

    @property
    def public_methods(self) -> List[str]:
        return sorted(
            {
                m.name
                for m in self.members
                if m.exclusion is None and m.kind == "method"
            }
        )

    @property
    def public_constructors(self) -> List[str]:
        return sorted(
            {
                m.name
                for m in self.members
                if m.exclusion is None and m.kind == "constructor"
            }
        )

    @property
    def public_surface(self) -> List[str]:
        """Public methods plus constructor names (class name)."""
        return sorted(set(self.public_methods) | set(self.public_constructors))

    def excluded_by_category(self) -> Dict[str, List[str]]:
        buckets: Dict[str, Set[str]] = {}
        for member in self.members:
            if not member.exclusion:
                continue
            buckets.setdefault(member.exclusion, set()).add(member.name)
        return {cat: sorted(names) for cat, names in sorted(buckets.items())}


@dataclass
class JavaFileSurface:
    path: Path
    package: str
    types: List[JavaTypeSurface] = field(default_factory=list)
    members_without_type: List[JavaMember] = field(default_factory=list)


@dataclass
class _Region:
    start: int
    end: int
    name: str
    kind: str  # class | interface | enum | anonymous
    visibility: str
    is_gui: bool
    is_public_type: bool


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _skip_string(text: str, i: int) -> int:
    quote = text[i]
    i += 1
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == quote:
            return i + 1
        i += 1
    return n


def strip_comments(text: str) -> Tuple[str, List[Tuple[int, int, str]]]:
    """Replace comments with spaces (newlines kept). Return (cleaned, comment spans).

    Spans are (start, end, comment_body) in the original/cleaned coordinate system
    (same indices, because comments are replaced in place).
    """
    n = len(text)
    out = list(text)
    comments: List[Tuple[int, int, str]] = []
    i = 0
    while i < n:
        c = text[i]
        if c in "\"'":
            i = _skip_string(text, i)
            continue
        if c == "/" and i + 1 < n:
            nxt = text[i + 1]
            if nxt == "/":
                start = i
                i += 2
                while i < n and text[i] != "\n":
                    i += 1
                comments.append((start, i, text[start:i]))
                for j in range(start, i):
                    if out[j] != "\n":
                        out[j] = " "
                continue
            if nxt == "*":
                start = i
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i = min(n, i + 2)
                comments.append((start, i, text[start:i]))
                for j in range(start, i):
                    if out[j] != "\n":
                        out[j] = " "
                continue
        i += 1
    return "".join(out), comments


def matching_braces(text: str) -> Dict[int, int]:
    """Map opening-brace index to matching close index, ignoring string literals."""
    stack: List[int] = []
    mapping: Dict[int, int] = {}
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            i = _skip_string(text, i)
            continue
        if c == "{":
            stack.append(i)
        elif c == "}":
            if stack:
                open_at = stack.pop()
                mapping[open_at] = i
        i += 1
    return mapping


def _next_body_brace(text: str, start: int, brace_map: Dict[int, int]) -> Optional[int]:
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            i = _skip_string(text, i)
            continue
        if c == "{":
            return i if i in brace_map else None
        if c == ";":
            return None
        i += 1
    return None


def _package_of(text: str) -> str:
    m = _PACKAGE_RE.search(text)
    return m.group(1) if m else ""


def _relpath(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_gui_package(package: str) -> bool:
    return package.startswith("org.uacalc.ui") or package.startswith("org.uacalc.nbui")


def _type_is_gui(name: str, header: str, package: str) -> bool:
    """True for UI packages, named GUI helpers, and real Swing widgets.

    Extending ``javax.swing.filechooser.FileFilter`` is not GUI: that is
    library file-filter API (``ExtFileFilter``). Matching any ``javax.swing``
    substring in the class header was a false positive.
    """
    if _is_gui_package(package) or name in _GUI_TYPE_NAMES:
        return True
    for super_name in _GUI_SUPERTYPES:
        if re.search(rf"\b{re.escape(super_name)}\b", header):
            return True
    return False


def _find_named_types(
    text: str, brace_map: Dict[int, int], package: str
) -> List[_Region]:
    regions: List[_Region] = []
    for m in _TYPE_DECL_RE.finditer(text):
        vis = m.group("vis") or "package"
        kind = m.group("kind")
        name = m.group("name")
        body_open = _next_body_brace(text, m.end(), brace_map)
        if body_open is None:
            continue
        body_close = brace_map[body_open]
        header = text[m.start() : body_open]
        is_gui = _type_is_gui(name, header, package)
        is_public = vis == "public" or (
            vis == "package" and kind == "interface" and not package
        )
        # Top-level types in a public compilation unit: the `public` keyword is
        # required for the file's main type. Nested types without a modifier are
        # package-private.
        regions.append(
            _Region(
                start=body_open,
                end=body_close,
                name=name,
                kind=kind,
                visibility=vis,
                is_gui=is_gui,
                is_public_type=vis == "public",
            )
        )
        _ = is_public
    return regions


def _skip_ws(text: str, i: int) -> int:
    n = len(text)
    while i < n and text[i].isspace():
        i += 1
    return i


def _skip_balanced(text: str, i: int, open_ch: str, close_ch: str) -> int:
    """Skip a balanced pair starting at ``open_ch``; return index after close."""
    if i >= len(text) or text[i] != open_ch:
        return i
    depth = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            i = _skip_string(text, i)
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _find_anonymous_classes(
    text: str, brace_map: Dict[int, int]
) -> List[_Region]:
    regions: List[_Region] = []
    n = len(text)
    i = 0
    while True:
        j = text.find("new", i)
        if j < 0:
            break
        # word boundary
        if j > 0 and (text[j - 1].isalnum() or text[j - 1] == "_"):
            i = j + 3
            continue
        after = j + 3
        if after < n and (text[after].isalnum() or text[after] == "_"):
            i = j + 3
            continue
        k = _skip_ws(text, after)
        # type name, possibly qualified / generic
        if k >= n or not (text[k].isalpha() or text[k] == "_"):
            i = j + 3
            continue
        while k < n:
            c = text[k]
            if c.isalnum() or c in "._":
                k += 1
                continue
            if c.isspace():
                k += 1
                continue
            if c == "<":
                k = _skip_balanced(text, k, "<", ">")
                continue
            break
        k = _skip_ws(text, k)
        # array creation: new Foo[ or new Foo[]
        if k < n and text[k] == "[":
            i = j + 3
            continue
        if k < n and text[k] == "(":
            k = _skip_balanced(text, k, "(", ")")
            k = _skip_ws(text, k)
        if k < n and text[k] == "{":
            close = brace_map.get(k)
            if close is not None:
                regions.append(
                    _Region(
                        start=k,
                        end=close,
                        name="<anonymous>",
                        kind="anonymous",
                        visibility="public",
                        is_gui=False,
                        is_public_type=False,
                    )
                )
        i = j + 3
    return regions


def _innermost(regions: List[_Region], pos: int) -> Optional[_Region]:
    containing = [r for r in regions if r.start < pos < r.end]
    if not containing:
        return None
    return max(containing, key=lambda r: r.start)


def _member_visibility(vis: Optional[str], enclosing: Optional[_Region]) -> str:
    if vis:
        return vis
    if enclosing is not None and enclosing.kind == "interface":
        return "public"
    return "package"


def _classify_member(
    *,
    name: str,
    kind: str,
    visibility: str,
    enclosing: Optional[_Region],
    commented: bool,
    package: str,
) -> Optional[str]:
    if commented:
        return COMMENTED_OUT
    if enclosing is not None and enclosing.kind == "anonymous":
        return ANONYMOUS_INNER_CLASS
    if enclosing is not None and enclosing.is_gui:
        return GUI
    if _is_gui_package(package):
        return GUI
    if enclosing is not None and not enclosing.is_public_type:
        return NON_PUBLIC_TYPE
    if kind == "method" and name == "main":
        return MAIN
    if kind == "method" and _LEGACY_NAME_RE.search(name):
        return LEGACY
    if visibility == "package":
        return PACKAGE_PRIVATE
    if visibility == "protected":
        return PROTECTED
    if visibility == "private":
        return NON_PUBLIC_TYPE
    return None


def _signature(vis: str, ret: Optional[str], name: str, params: str) -> str:
    params_clean = " ".join(params.split())
    if ret:
        return f"{vis} {ret.strip()} {name}({params_clean})".strip()
    return f"{vis} {name}({params_clean})".strip()


def _looks_like_type_decl(ret: Optional[str], name: str) -> bool:
    if name in ("class", "interface", "enum"):
        return True
    if (ret or "").strip() in ("class", "interface", "enum"):
        return True
    return False


def scan_java_source(
    text: str, *, path: Optional[Path] = None, package: Optional[str] = None
) -> JavaFileSurface:
    """Scan one compilation unit. ``path`` is used for GUI-package / relpath."""
    path = path or Path("<memory>")
    pkg = package if package is not None else _package_of(text)
    cleaned, comments = strip_comments(text)
    brace_map = matching_braces(cleaned)
    named = _find_named_types(cleaned, brace_map, pkg)
    anonymous = _find_anonymous_classes(cleaned, brace_map)
    regions = named + anonymous

    file_is_gui = _is_gui_package(pkg)
    rel = _relpath(path) if path.name != "<memory>" else str(path)

    types_by_name: Dict[str, JavaTypeSurface] = {}
    type_order: List[str] = []
    for region in named:
        fqcn = f"{pkg}.{region.name}" if pkg else region.name
        if region.name not in types_by_name:
            types_by_name[region.name] = JavaTypeSurface(
                fqcn=fqcn,
                simple_name=region.name,
                kind=region.kind,
                visibility=region.visibility,
                package=pkg,
                source_relpath=rel,
                is_gui=region.is_gui or file_is_gui,
            )
            type_order.append(region.name)

    def attach(member: JavaMember, type_name: Optional[str]) -> None:
        if type_name and type_name in types_by_name:
            types_by_name[type_name].members.append(member)
        elif type_order:
            types_by_name[type_order[0]].members.append(member)
        else:
            orphan_members.append(member)

    orphan_members: List[JavaMember] = []

    # Live members from the uncommented source.
    for m in _MEMBER_RE.finditer(cleaned):
        name = m.group("name")
        ret = m.group("ret")
        if name in _SKIP_MEMBER_NAMES or _looks_like_type_decl(ret, name):
            continue
        if ret and _BAD_RET_RE.search(ret):
            continue
        vis_raw = m.group("vis")
        mods = m.group("mods") or ""
        enclosing = _innermost(regions, m.start())
        vis = _member_visibility(vis_raw, enclosing)
        # Skip obvious field-like false positives: no return type and not a ctor.
        enclosing_name = enclosing.name if enclosing and enclosing.kind != "anonymous" else (
            enclosing.name if enclosing else None
        )
        named_enclosing = None
        if enclosing is not None and enclosing.kind != "anonymous":
            named_enclosing = enclosing.name
        elif enclosing is not None and enclosing.kind == "anonymous":
            outer = _innermost(
                [r for r in named],
                enclosing.start,
            )
            named_enclosing = outer.name if outer else (type_order[0] if type_order else None)
        else:
            named_enclosing = type_order[0] if type_order else None

        is_ctor = named_enclosing is not None and name == named_enclosing
        if enclosing is not None and enclosing.kind == "anonymous":
            is_ctor = False
        if not (ret or "").strip() and not is_ctor:
            continue
        kind = "constructor" if is_ctor else "method"
        exclusion = _classify_member(
            name=name,
            kind=kind,
            visibility=vis,
            enclosing=enclosing,
            commented=False,
            package=pkg,
        )
        member = JavaMember(
            name=name,
            kind=kind,
            enclosing_type=named_enclosing or "<unknown>",
            visibility=vis,
            exclusion=exclusion,
            line=_line_number(text, m.start()),
            signature=_signature(vis, ret, name, m.group("params") or ""),
            is_static="static" in mods,
        )
        attach(member, named_enclosing)

    # Commented-out public members (same coordinates as cleaned source).
    seen_commented: Set[Tuple[str, str, int]] = set()
    for start, _end, body in comments:
        enclosing = _innermost(regions, start)
        named_enclosing = None
        if enclosing is not None and enclosing.kind != "anonymous":
            named_enclosing = enclosing.name
        elif enclosing is not None:
            outer = _innermost([r for r in named], enclosing.start)
            named_enclosing = outer.name if outer else (type_order[0] if type_order else None)
        else:
            named_enclosing = type_order[0] if type_order else None
        for cm in _COMMENTED_PUBLIC_RE.finditer(body):
            name = cm.group(2)
            ret = cm.group(1)
            if name in _SKIP_MEMBER_NAMES or _looks_like_type_decl(ret, name):
                continue
            is_ctor = named_enclosing is not None and name == named_enclosing
            if not (ret or "").strip() and not is_ctor:
                continue
            kind = "constructor" if is_ctor else "method"
            key = (named_enclosing or "", name, kind == "constructor")
            if key in seen_commented:
                continue
            seen_commented.add(key)
            member = JavaMember(
                name=name,
                kind=kind,
                enclosing_type=named_enclosing or "<unknown>",
                visibility="public",
                exclusion=COMMENTED_OUT,
                line=_line_number(text, start + cm.start()),
                signature=_signature("public", ret, name, ""),
            )
            attach(member, named_enclosing)

    return JavaFileSurface(
        path=path,
        package=pkg,
        types=[types_by_name[n] for n in type_order],
        members_without_type=orphan_members,
    )


def scan_java_file(path: Path) -> JavaFileSurface:
    text = path.read_text(encoding="utf-8", errors="replace")
    return scan_java_source(text, path=path)


def iter_org_uacalc_java(root: Optional[Path] = None) -> Iterable[Path]:
    base = root or JAVA_ROOT
    for path in sorted(base.rglob("*.java")):
        if path.name == "package-info.java":
            continue
        yield path


def scan_package_dir(java_dir: Path, *, recursive: bool = False) -> List[JavaTypeSurface]:
    types: List[JavaTypeSurface] = []
    iterator = java_dir.rglob("*.java") if recursive else java_dir.glob("*.java")
    for path in sorted(iterator):
        if path.name == "package-info.java":
            continue
        types.extend(scan_java_file(path).types)
    return types


def public_surface_names(types: Iterable[JavaTypeSurface]) -> Set[str]:
    names: Set[str] = set()
    for t in types:
        names.update(t.public_surface)
    return names


def excluded_names_by_category(
    types: Iterable[JavaTypeSurface],
) -> Dict[str, Set[str]]:
    buckets: Dict[str, Set[str]] = {cat: set() for cat in EXCLUSION_CATEGORIES}
    for t in types:
        for member in t.members:
            if member.exclusion:
                buckets.setdefault(member.exclusion, set()).add(member.name)
    return {k: v for k, v in buckets.items() if v}


def excluded_occurrence_counts(
    types: Iterable[JavaTypeSurface],
) -> Dict[str, int]:
    """How many member declarations were excluded in each category."""
    counts: Dict[str, int] = {}
    for t in types:
        for member in t.members:
            if member.exclusion:
                counts[member.exclusion] = counts.get(member.exclusion, 0) + 1
    return counts


def format_exclusion_summary(
    types: Iterable[JavaTypeSurface], *, indent: str = "  "
) -> List[str]:
    buckets = excluded_names_by_category(types)
    counts = excluded_occurrence_counts(types)
    lines: List[str] = []
    for cat in EXCLUSION_CATEGORIES:
        names = buckets.get(cat)
        if not names:
            continue
        reason = CATEGORY_REASONS.get(cat, cat)
        sample = ", ".join(sorted(names)[:12])
        extra = ""
        if len(names) > 12:
            extra = f", ... +{len(names) - 12}"
        n = counts.get(cat, len(names))
        lines.append(
            f"{indent}- {cat} ({n} members, {len(names)} names): {reason}. "
            f"e.g. {sample}{extra}"
        )
    return lines
