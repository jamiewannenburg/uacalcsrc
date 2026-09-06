"""Jython-style wrappers around ``uacalc_lib.io`` (CPython only)."""

from __future__ import annotations

import os
from typing import Any, List, Optional, Union

import uacalc_lib as _uacalc_lib

_io = getattr(_uacalc_lib, "io")
_LibAlgebraReader = _io.AlgebraReader
_LibAlgebraWriter = _io.AlgebraWriter
_LibMace4Reader = _io.Mace4Reader
_LibBadAlgebraFileException = _io.BadAlgebraFileException


def _coerce_path(path_or_file: Any) -> str:
    if isinstance(path_or_file, (str, os.PathLike)):
        return os.fspath(path_or_file)
    if hasattr(path_or_file, "name") and isinstance(getattr(path_or_file, "name", None), str):
        return path_or_file.name
    raise TypeError(
        "expected a path string or path-like object, got {!r}".format(type(path_or_file))
    )


def _coerce_stream_bytes(stream: Any) -> bytes:
    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)
    if isinstance(stream, str):
        return stream.encode("utf-8")
    if hasattr(stream, "read"):
        data = stream.read()
        if isinstance(data, str):
            return data.encode("utf-8")
        return bytes(data)
    raise TypeError(
        "expected bytes, str, or a readable stream, got {!r}".format(type(stream))
    )


class AlgebraIO:
    """Static helpers matching ``org.uacalc.io.AlgebraIO``."""

    @staticmethod
    def readAlgebraFile(path_or_file: Any) -> Any:
        # Use AlgebraReader so description and other SAX fields survive (the
        # module-level read_algebra_file rebuilds a bare BasicAlgebra).
        return AlgebraReader(_coerce_path(path_or_file)).readAlgebraFile()

    @staticmethod
    def readAlgebraFromStream(stream: Any) -> Any:
        return AlgebraReader(_coerce_stream_bytes(stream)).readAlgebraFromStream()

    @staticmethod
    def readAlgebraListFile(path_or_file: Any) -> List[Any]:
        return _io.read_algebra_list_file(_coerce_path(path_or_file))

    @staticmethod
    def readAlgebraListFromStream(stream: Any) -> Any:
        return _io.read_algebra_list_from_stream(_coerce_stream_bytes(stream))

    @staticmethod
    def convertToXML(path_or_file: Any) -> None:
        return _io.convert_to_xml(_coerce_path(path_or_file))

    @staticmethod
    def writeAlgebraFile(algebra: Any, path_or_file: Any, oldStyle: Optional[bool] = None) -> None:
        path = _coerce_path(path_or_file)
        # Unwrap org.uacalc.alg BasicAlgebra Jython compat wrapper if present.
        alg = getattr(algebra, "_inner", algebra)
        use_old_style = bool(oldStyle) if oldStyle is not None else False
        if use_old_style:
            return _io.write_algebra_file_with_style(alg, path, True)
        # Java AlgebraIO.writeAlgebraFile writes XML to the given path whenever
        # the file has an extension (including .ua). uacalc_lib.write_algebra_file
        # appends ".xml" for non-.xml suffixes, so use AlgebraWriter instead.
        return _LibAlgebraWriter.write_algebra_xml_to_file(alg, path)


class AlgebraReader:
    """Instance reader matching ``org.uacalc.io.AlgebraReader``."""

    def __init__(self, path_or_stream: Any) -> None:
        if isinstance(path_or_stream, (bytes, bytearray)):
            self._path: Optional[str] = None
            self._stream_data = bytes(path_or_stream)
            self._inner = _LibAlgebraReader.new_from_stream(self._stream_data)
        elif hasattr(path_or_stream, "read"):
            self._path = None
            self._stream_data = _coerce_stream_bytes(path_or_stream)
            self._inner = _LibAlgebraReader.new_from_stream(self._stream_data)
        elif isinstance(path_or_stream, str) and os.path.isfile(path_or_stream):
            self._path = path_or_stream
            self._stream_data = None
            self._inner = _LibAlgebraReader.new_from_file(self._path)
        elif isinstance(path_or_stream, str):
            self._path = None
            self._stream_data = path_or_stream.encode("utf-8")
            self._inner = _LibAlgebraReader.new_from_stream(self._stream_data)
        else:
            self._path = _coerce_path(path_or_stream)
            self._stream_data = None
            self._inner = _LibAlgebraReader.new_from_file(self._path)

    def readAlgebraFile(self) -> Any:
        return self.read_algebra_file()

    def read_algebra_file(self) -> Any:
        if self._path is not None:
            result = self._inner.read_algebra_file()
        else:
            result = self._inner.read_algebra_from_stream(self._stream_data)
        if result is None:
            raise ValueError("no algebra read from source")
        return result

    def readAlgebraFromStream(self) -> Any:
        return self.read_algebra_from_stream()

    def read_algebra_from_stream(self) -> Any:
        if self._stream_data is None:
            raise ValueError("reader was not constructed from a stream")
        result = self._inner.read_algebra_from_stream(self._stream_data)
        if result is None:
            raise ValueError("no algebra read from stream")
        return result

    def readAlgebraListFile(self) -> List[Any]:
        return self.read_algebra_list_file()

    def read_algebra_list_file(self) -> List[Any]:
        if self._path is not None:
            return self._inner.read_algebra_list_from_file(self._path)
        return self._inner.read_algebra_list_from_stream(self._stream_data)

    def readAlgebraListFromStream(self) -> List[Any]:
        return self.read_algebra_list_from_stream()

    def read_algebra_list_from_stream(self) -> List[Any]:
        if self._stream_data is None:
            raise ValueError("reader was not constructed from a stream")
        return self._inner.read_algebra_list_from_stream(self._stream_data)


class AlgebraWriter:
    """Writer matching ``org.uacalc.io.AlgebraWriter`` instance API."""

    def __init__(self, algebra: Any, path_or_writer: Any) -> None:
        self._algebra = getattr(algebra, "_inner", algebra)
        if hasattr(path_or_writer, "write"):
            raise NotImplementedError(
                "AlgebraWriter with a custom writer is not bound in uacalc_lib"
            )
        self._path = _coerce_path(path_or_writer)

    def writeAlgebraXML(self) -> None:
        return self.write_algebra_xml()

    def write_algebra_xml(self) -> None:
        return _LibAlgebraWriter.write_algebra_xml_to_file(self._algebra, self._path)

    def writeAlgebra(self) -> None:
        return self.write_algebra()

    def write_algebra(self) -> None:
        return _LibAlgebraWriter.write_algebra_to_file(self._algebra, self._path)

    def writeBasicAlgebra(self) -> None:
        return self.write_basic_algebra()

    def write_basic_algebra(self) -> None:
        return _LibAlgebraWriter.write_basic_algebra_to_file(self._algebra, self._path)


class Mace4Reader:
    """Mace4 parser matching ``org.uacalc.io.Mace4Reader``.

    Jython constructs ``Mace4Reader(stream)`` and calls ``parseAlgebra()``.
    Static helpers from ``uacalc_lib.io.Mace4Reader`` are re-exported so callers
    can use either the Java constructor or the binding factory methods.
    """

    new_from_file = staticmethod(_LibMace4Reader.new_from_file)
    new_from_stream = staticmethod(_LibMace4Reader.new_from_stream)
    parse_algebra_from_file = staticmethod(_LibMace4Reader.parse_algebra_from_file)

    def __init__(self, stream: Any) -> None:
        self._data = _coerce_stream_bytes(stream)
        self._inner = _LibMace4Reader.new_from_stream(self._data)

    def parseAlgebra(self) -> Any:
        return self.parse_algebra()

    def parse_algebra(self) -> Any:
        result = self._inner.parse_algebra_from_stream(self._data)
        if result is None:
            raise ValueError("no algebra parsed from Mace4 stream")
        return result

    def parseAlgebraList(self) -> List[Any]:
        return self.parse_algebra_list()

    def parse_algebra_list(self) -> List[Any]:
        return self._inner.parse_algebra_list_from_stream(self._data)


BadAlgebraFileException = _LibBadAlgebraFileException
ExtFileFilter = _io.ExtFileFilter
