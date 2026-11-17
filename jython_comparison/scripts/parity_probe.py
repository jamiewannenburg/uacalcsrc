# coding: utf-8
"""Shared probe helpers for dual-runtime jython_comparison scripts.

Exception lines use ``EXC <section>: <Category>`` with no message text so
Jython (Java throwables) and CPython agree on stdout.

Category mapping (Python name -> stable token):
  AttributeError, TypeError -> NullPointerException
  IndexError -> IndexOutOfBoundsException
  KeyError -> NoSuchElementException
  ValueError -> IllegalArgumentException
  NotImplementedError -> UnsupportedOperationException
  IOError, OSError -> IOException

Java simple class names (NullPointerException, etc.) pass through unchanged.
"""
from __future__ import print_function

import sys

if sys.platform.startswith("java"):
    from java.lang import Throwable as JavaThrowable

    _CATCH = (Exception, JavaThrowable)
else:
    _CATCH = (Exception,)

_PYTHON_TO_TOKEN = {
    "AttributeError": "NullPointerException",
    "TypeError": "NullPointerException",
    "IndexError": "IndexOutOfBoundsException",
    "KeyError": "NoSuchElementException",
    "ValueError": "IllegalArgumentException",
    "NotImplementedError": "UnsupportedOperationException",
    "IOError": "IOException",
    "OSError": "IOException",
    "FileNotFoundError": "IOException",
}


def exception_token(exc):
    """Map an exception instance to a stable category name."""
    if exc is None:
        return "Exception"
    name = type(exc).__name__
    if "." in name:
        name = name.rsplit(".", 1)[-1]
    return _PYTHON_TO_TOKEN.get(name, name)


def probe(section, thunk, printer=None):
    """Run thunk; print ``section=value`` or ``EXC section: Category``."""
    try:
        value = thunk()
    except _CATCH:
        exc = sys.exc_info()[1]
        print("EXC %s: %s" % (section, exception_token(exc)))
        return
    if printer is not None:
        printer(value)
        return
    try:
        text = value if isinstance(value, (str, int, bool)) or value is None else str(value)
    except _CATCH:
        exc = sys.exc_info()[1]
        print("EXC %s: %s" % (section, exception_token(exc)))
        return
    print("%s=%s" % (section, text))


def section(section_name, thunk):
    """Run thunk for side-effect prints; on failure emit one EXC line."""
    try:
        thunk()
    except _CATCH:
        exc = sys.exc_info()[1]
        print("EXC %s: %s" % (section_name, exception_token(exc)))