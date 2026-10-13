"""Java-named exceptions for the CPython ``org.uacalc`` shim.

Jython raises ``java.lang.*`` / ``java.io.*`` types. The Rust bindings surface
``ValueError`` / ``FileNotFoundError``. The shim translates at the wrapper
boundary so exception *names* match Java; Python ``except OSError`` /
``except ValueError`` still work via inheritance.
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional


class JavaException(Exception):
    """Base for Java-like exceptions raised by the CPython org.uacalc shim."""


class RuntimeException(JavaException):
    """java.lang.RuntimeException."""


class IllegalArgumentException(ValueError, RuntimeException):
    """java.lang.IllegalArgumentException."""


class NumberFormatException(IllegalArgumentException):
    """java.lang.NumberFormatException."""


class NullPointerException(TypeError, RuntimeException):
    """java.lang.NullPointerException."""


class ClassCastException(TypeError, RuntimeException):
    """java.lang.ClassCastException."""


class UnsupportedOperationException(RuntimeException):
    """java.lang.UnsupportedOperationException."""


class IndexOutOfBoundsException(IndexError, RuntimeException):
    """java.lang.IndexOutOfBoundsException."""


class IOException(OSError, JavaException):
    """java.io.IOException."""


class FileNotFoundException(FileNotFoundError, IOException):
    """java.io.FileNotFoundException.

    Subclasses both ``FileNotFoundError`` (``OSError`` / ``IOError``) and the
    Java-like ``IOException`` so ``except OSError`` still catches it.
    """


_PARSE_INT_RE = re.compile(r"Failed to parse (\w+):", re.I)
_XML_TAG_TO_LOOKUP = {
    "size": "cardinality",
    "cardinality": "cardinality",
    "arity": "arity",
    "power": "power",
}


def java_file_not_found_message(path: Any, exc: Optional[BaseException] = None) -> str:
    """Match ``java.io.FileNotFoundException``: ``path (No such file or directory)``."""
    detail = getattr(exc, "strerror", None) or "No such file or directory"
    return "{} ({})".format(path, detail)


def java_number_format_message(token: str) -> str:
    """Match ``Integer.parseInt``: ``For input string: "…"``."""
    return 'For input string: "{}"'.format(token)


def _xml_tag_text(source: Any, tag: str) -> Optional[str]:
    if not source or not tag:
        return None
    text = None
    if isinstance(source, (bytes, bytearray)):
        text = bytes(source).decode("utf-8", "replace")
    elif isinstance(source, str) and os.path.isfile(source):
        try:
            with open(source, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read(8192)
        except OSError:
            return None
    elif isinstance(source, str):
        text = source
    if not text:
        return None
    pattern = r"<{0}>\s*([^<]*?)\s*</{0}>".format(re.escape(tag))
    match = re.search(pattern, text, re.I)
    if match:
        return match.group(1).strip()
    return None


def translate_io_error(
    exc: BaseException,
    path: Optional[str] = None,
    stream_text: Any = None,
) -> None:
    """Reraise *exc* as a Java-named type when that mapping is a shim concern.

    Leaves library-owned mismatches (missing file reported as
    ``No algebras found in file``) unchanged.
    """
    if isinstance(
        exc,
        (NumberFormatException, FileNotFoundException, IllegalArgumentException),
    ):
        raise exc
    if isinstance(exc, FileNotFoundError):
        location = path or getattr(exc, "filename", None)
        raise FileNotFoundException(java_file_not_found_message(location, exc)) from exc
    if isinstance(exc, ValueError):
        msg = str(exc)
        parsed = _PARSE_INT_RE.search(msg)
        looks_nfe = parsed is not None or "invalid digit" in msg.lower()
        if looks_nfe:
            raw_tag = parsed.group(1) if parsed else "cardinality"
            xml_tag = _XML_TAG_TO_LOOKUP.get(raw_tag.lower(), raw_tag)
            token = _xml_tag_text(path, xml_tag) or _xml_tag_text(stream_text, xml_tag)
            if token is not None:
                raise NumberFormatException(java_number_format_message(token)) from exc
            raise NumberFormatException(msg) from exc
    raise exc


def translate_illegal_argument(exc: BaseException) -> None:
    if isinstance(exc, IllegalArgumentException):
        raise exc
    if isinstance(exc, ValueError):
        raise IllegalArgumentException(str(exc)) from exc
    raise exc
