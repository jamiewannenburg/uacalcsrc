"""Parse LatDraw ``.lat`` S-expression files (``org.latdraw.orderedset.InputLattice``)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_INT_RE = re.compile(r"^-?\d+$")


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in "()":
            tokens.append(c)
            i += 1
            continue
        if c.isspace():
            i += 1
            continue
        j = i
        while j < n and not text[j].isspace() and text[j] not in "()":
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def _parse_sexpr(tokens: list[str], pos: list[int]) -> Any:
    if pos[0] >= len(tokens) or tokens[pos[0]] != "(":
        raise ValueError("expected '('")
    pos[0] += 1
    if pos[0] < len(tokens) and tokens[pos[0]] == ")":
        pos[0] += 1
        return []
    if pos[0] >= len(tokens):
        raise ValueError("unexpected end of input in list")
    head = _parse_atom(tokens[pos[0]])
    pos[0] += 1
    rest: list[Any] = []
    while pos[0] < len(tokens) and tokens[pos[0]] != ")":
        if tokens[pos[0]] == "(":
            rest.append(_parse_sexpr(tokens, pos))
        else:
            rest.append(_parse_atom(tokens[pos[0]]))
            pos[0] += 1
    if pos[0] >= len(tokens) or tokens[pos[0]] != ")":
        raise ValueError("expected ')'")
    pos[0] += 1
    if not rest:
        return head
    return [head, *rest]


def _parse_atom(tok: str) -> str | int:
    if _INT_RE.match(tok):
        return int(tok)
    if tok.startswith("{") and tok.endswith("}"):
        tok = tok[1:-1]
    return tok


def _normalize_name(raw: str | int) -> str:
    s = str(raw)
    if re.match(r"^\{?B_1\}+$", s):
        return "B_1"
    if s.startswith("{") and s.endswith("}") and "{" not in s[1:-1]:
        s = s[1:-1]
    return s


def _filter_from_element(child: list | str | int) -> list[int | str]:
    if not isinstance(child, list) or len(child) < 2:
        return []
    filt = child[1]
    if filt == [] or filt is None:
        return []
    if isinstance(filt, list):
        return [x for x in filt if not isinstance(x, list)]
    return [filt]


def parse_lat_file(path: str | Path) -> tuple[str, list[int | str], list[list[int | str]]]:
    """
    Return ``(name, labels, upper_covers_list)`` matching Java ``InputLattice``.

    ``upper_covers_list[i]`` is the filter for ``labels[i]`` (elements weakly above it).
    """
    text = Path(path).read_text(encoding="utf-8", errors="replace").strip()
    if not text or text == ")":
        raise ValueError(f"empty .lat file: {path}")
    tokens = _tokenize(text)
    if not tokens:
        raise ValueError(f"empty .lat file: {path}")
    pos = [0]
    tree = _parse_sexpr(tokens, pos)
    if not isinstance(tree, list) or len(tree) < 1:
        raise ValueError(f"invalid .lat structure: {path}")
    name = _normalize_name(tree[0])
    labels: list[int | str] = []
    filters: list[list[int | str]] = []
    for child in tree[1:]:
        if not isinstance(child, list):
            continue
        label = child[0] if child else None
        if label is None:
            continue
        labels.append(label)
        filters.append(_filter_from_element(child))
    if len(labels) != len(filters):
        raise ValueError(f"label/filter length mismatch in {path}")
    return name, labels, filters