"""Jython-facing helpers for ``org.uacalc.util`` (CPython only).

Java-shaped constructors, camelCase statics, and in-place incrementors.
Library logic stays in ``uacalc_lib`` where it already matches; SequenceGenerator
incrementors, Horner overloads, and ArrayString recursion are implemented here
to match ``org/uacalc/util/*.java``.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, List, Optional, Sequence

from org.uacalc._exceptions import (
    ArrayIndexOutOfBoundsException,
    IllegalArgumentException,
    IndexOutOfBoundsException,
    NullPointerException,
    UnsupportedOperationException,
    translate_illegal_argument,
)


def _bind(cls: Any, name: str, impl: Any) -> None:
    if cls is None:
        return
    try:
        setattr(cls, name, impl)
    except (TypeError, AttributeError):
        pass


def _npe_null(value: Any, msg: str = "") -> None:
    if value is None:
        raise NullPointerException(msg)


def _as_int_list(arr: Any) -> List[int]:
    if arr is None:
        raise NullPointerException()
    return [int(x) for x in arr]


def _write_dest(dest: Any, values: Sequence[int]) -> Any:
    if dest is None:
        return list(values)
    if len(dest) != len(values):
        raise ArrayIndexOutOfBoundsException()
    for i, v in enumerate(values):
        dest[i] = int(v)
    return dest


def _java_hash_code(values: Sequence[int]) -> int:
    ans = 1
    for x in values:
        ans = ((ans * 31) + int(x)) & 0xFFFFFFFF
        if ans >= 0x80000000:
            ans -= 0x100000000
    return ans


class _InPlaceIncrementor(object):
    """ArrayIncrementor that mutates the caller's buffer, matching Java."""

    def __init__(self, increment: Callable[[], bool]) -> None:
        self._increment = increment

    def increment(self) -> bool:
        return bool(self._increment())


class _LexComparator(object):
    def compare(self, ia0: Any, ia1: Any) -> int:
        n0 = int(ia0.universeSize() if hasattr(ia0, "universeSize") else ia0.universe_size())
        n1 = int(ia1.universeSize() if hasattr(ia1, "universeSize") else ia1.universe_size())
        m = n0 if n0 < n1 else n1
        for i in range(m):
            v0 = int(ia0.get(i))
            v1 = int(ia1.get(i))
            if v0 < v1:
                return -1
            if v0 > v1:
                return 1
        if n0 < n1:
            return -1
        if n0 > n1:
            return 1
        return 0


# ---------------------------------------------------------------------------
# Sequence incrementors (Java SequenceGenerator, in-place)
# ---------------------------------------------------------------------------


def _inc_nondecreasing(a: Any, max_v: int, last_min: int) -> bool:
    if a[0] >= max_v:
        return False
    length = len(a)
    for i in range(length - 1, -1, -1):
        if a[i] < max_v:
            k = int(a[i]) + 1
            for j in range(i, length):
                a[j] = k
            if a[length - 1] < last_min:
                a[length - 1] = last_min
            break
    return True


def _inc_increasing(a: Any, maxs: Sequence[int]) -> bool:
    length = len(a)
    for i in range(length - 1, -1, -1):
        if a[i] < maxs[i]:
            v = int(a[i]) + 1
            for j in range(i, length):
                a[j] = v
                v += 1
            return True
    return False


def _inc_sequence(a: Any, maxs: Sequence[int]) -> bool:
    length = len(a)
    for i in range(length - 1, -1, -1):
        if a[i] < maxs[i]:
            a[i] = int(a[i]) + 1
            for j in range(i + 1, length):
                a[j] = 0
            return True
    return False


def _inc_sequence_min(a: Any, max_v: int, min_v: int) -> bool:
    length = len(a)
    for i in range(length - 1, -1, -1):
        if a[i] < max_v:
            a[i] = int(a[i]) + 1
            for j in range(i + 1, length):
                a[j] = 0
            ok = False
            for j in range(i, -1, -1):
                if a[j] >= min_v:
                    ok = True
                    break
            if not ok:
                a[length - 1] = min_v
            return True
    return False


def _inc_left(a: Any, max_v: int) -> bool:
    length = len(a)
    for i in range(length):
        if a[i] < max_v:
            a[i] = int(a[i]) + 1
            for j in range(i - 1, -1, -1):
                a[j] = 0
            return True
    return False


def _set_maxs(maxs: List[int], ro_indeces: Sequence[int]) -> None:
    index = 0
    max_v = 0
    for i in range(1, len(ro_indeces)):
        k = int(ro_indeces[i]) - int(ro_indeces[i - 1]) - 1
        for _j in range(k):
            maxs[index] = max_v
            index += 1
        max_v += 1
    for i in range(index, len(maxs)):
        maxs[i] = max_v


def _inc_increasing_roots(root_indeces: List[int], max_v: int) -> bool:
    length = len(root_indeces)
    maxs = [0] * length
    value = max_v
    for i in range(length - 1, -1, -1):
        maxs[i] = value
        value -= 1
    return _inc_increasing(root_indeces, maxs)


def _make_partition_incrementor(a: Any, num_blocks: int) -> Callable[[], bool]:
    size = len(a)
    root_indeces = [0] * num_blocks
    index = 0
    for i in range(size):
        if a[i] == i:
            root_indeces[index] = i
            index += 1
    num_non_roots = size - num_blocks
    non_root_indeces = [0] * num_non_roots
    index = 0
    for i in range(size):
        if a[i] != i:
            non_root_indeces[index] = i
            index += 1
    maxs = [0] * num_non_roots
    _set_maxs(maxs, root_indeces)
    non_roots_root_indeces = [0] * num_non_roots

    def increment() -> bool:
        for i in range(num_non_roots - 1, -1, -1):
            if non_roots_root_indeces[i] < maxs[i]:
                non_roots_root_indeces[i] += 1
                a[non_root_indeces[i]] = root_indeces[non_roots_root_indeces[i]]
                for j in range(i + 1, num_non_roots):
                    a[non_root_indeces[j]] = 0
                    non_roots_root_indeces[j] = 0
                return True
        if not _inc_increasing_roots(root_indeces, size - 1):
            return False
        if root_indeces[0] != 0:
            return False
        for i in range(size):
            a[i] = 0
        for i in range(num_blocks):
            a[root_indeces[i]] = root_indeces[i]
        index = 0
        for i in range(size):
            if a[i] != i:
                non_root_indeces[index] = i
                index += 1
        for i in range(num_non_roots):
            non_roots_root_indeces[i] = 0
        _set_maxs(maxs, root_indeces)
        return True

    return increment


class SequenceGenerator(object):
    """Java ``org.uacalc.util.SequenceGenerator`` static factories."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def nondecreasingSequenceIncrementor(a, max, lastMin=0):
        max_v = int(max)
        last_min = int(lastMin)
        return _InPlaceIncrementor(lambda: _inc_nondecreasing(a, max_v, last_min))

    @staticmethod
    def increasingSequenceIncrementorOld(a, max):
        length = len(a)
        a2 = [0] * length
        max_v = int(max) + 1 - length
        nondec = SequenceGenerator.nondecreasingSequenceIncrementor(a2, max_v)

        def increment() -> bool:
            if not nondec.increment():
                return False
            for i in range(length):
                a[i] = int(a2[i]) + i
            return True

        return _InPlaceIncrementor(increment)

    @staticmethod
    def increasingSequenceIncrementor(a, max):
        length = len(a)
        maxs = [0] * length
        value = int(max)
        for i in range(length - 1, -1, -1):
            maxs[i] = value
            value -= 1
        return _InPlaceIncrementor(lambda: _inc_increasing(a, maxs))

    @staticmethod
    def sequenceIncrementor(a, max, min=None, jump=None):
        if isinstance(max, (list, tuple)):
            maxs = [int(x) for x in max]
            return _InPlaceIncrementor(lambda: _inc_sequence(a, maxs))
        max_v = int(max)
        if min is None:
            maxs = [max_v] * len(a)
            return _InPlaceIncrementor(lambda: _inc_sequence(a, maxs))
        min_v = int(min)
        if jump is None:
            return _InPlaceIncrementor(lambda: _inc_sequence_min(a, max_v, min_v))
        jump_v = int(jump)

        def increment() -> bool:
            for _k in range(jump_v):
                if not _inc_sequence_min(a, max_v, min_v):
                    return False
            return True

        return _InPlaceIncrementor(increment)

    @staticmethod
    def leftSequenceIncrementor(a, max):
        max_v = int(max)
        return _InPlaceIncrementor(lambda: _inc_left(a, max_v))

    @staticmethod
    def initialPartition(size, numBlocks):
        size_i = int(size)
        num = int(numBlocks)
        ans = [0] * size_i
        for i in range(num):
            ans[i] = i
        return ans

    @staticmethod
    def partitionArrayIncrementor(a, numBlocks):
        return _InPlaceIncrementor(_make_partition_incrementor(a, int(numBlocks)))


# Keep snake_case names used by existing CPython callers.
SequenceGenerator.nondecreasing_sequence_incrementor = (  # type: ignore[attr-defined]
    SequenceGenerator.nondecreasingSequenceIncrementor
)
SequenceGenerator.increasing_sequence_incrementor = (  # type: ignore[attr-defined]
    SequenceGenerator.increasingSequenceIncrementor
)
SequenceGenerator.sequence_incrementor = SequenceGenerator.sequenceIncrementor  # type: ignore[attr-defined]
SequenceGenerator.left_sequence_incrementor = (  # type: ignore[attr-defined]
    SequenceGenerator.leftSequenceIncrementor
)
SequenceGenerator.initial_partition = SequenceGenerator.initialPartition  # type: ignore[attr-defined]
SequenceGenerator.partition_array_incrementor = (  # type: ignore[attr-defined]
    SequenceGenerator.partitionArrayIncrementor
)


# ---------------------------------------------------------------------------
# Horner (all Java overloads)
# ---------------------------------------------------------------------------


class Horner(object):
    """Java ``org.uacalc.util.Horner`` static methods."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def horner(args, sizes_or_size):
        _npe_null(args)
        args_l = _as_int_list(args)
        if isinstance(sizes_or_size, (list, tuple)):
            if not args_l:
                raise ArrayIndexOutOfBoundsException()
            k = len(args_l)
            ans = args_l[k - 1]
            for i in range(k - 2, -1, -1):
                ans = int(sizes_or_size[i]) * ans + args_l[i]
            return ans
        size = int(sizes_or_size)
        ans = 0
        for i in range(len(args_l) - 1, -1, -1):
            ans = size * ans + args_l[i]
        return ans

    @staticmethod
    def hornerInv(k, sizes_or_size, dest_or_length=None, dest=None):
        k = int(k)
        if isinstance(sizes_or_size, (list, tuple)):
            sizes = [int(x) for x in sizes_or_size]
            n = len(sizes)
            if dest_or_length is None:
                ans = [0] * n
            else:
                ans = dest_or_length
                if len(ans) < n:
                    raise ArrayIndexOutOfBoundsException()
            if n == 0:
                raise ArrayIndexOutOfBoundsException()
            for i in range(n - 1):
                ans[i] = k % sizes[i]
                k = (k - int(ans[i])) // sizes[i]
            ans[n - 1] = k
            return ans if dest_or_length is not None else list(ans)
        size = int(sizes_or_size)
        if dest_or_length is None:
            raise TypeError("hornerInv(k, size, length[, dest]) requires length")
        n = int(dest_or_length)
        if dest is None:
            ans = [0] * n
        else:
            ans = dest
            if len(ans) < n:
                raise ArrayIndexOutOfBoundsException()
        if n == 0:
            return ans
        for i in range(n - 1):
            ans[i] = k % size
            k = (k - int(ans[i])) // size
        ans[n - 1] = k
        return ans if dest is not None else list(ans)

    @staticmethod
    def reverseArray(arr):
        _npe_null(arr)
        arr_l = _as_int_list(arr)
        return list(reversed(arr_l))

    @staticmethod
    def leftRightReverse(values, algSize, arity):
        _npe_null(values)
        values_l = _as_int_list(values)
        alg_size = int(algSize)
        ar = int(arity)
        ans = [0] * len(values_l)
        for i in range(len(values_l)):
            foo = Horner.reverseArray(Horner.hornerInv(i, alg_size, ar))
            i_prime = Horner.horner(foo, alg_size)
            ans[i_prime] = values_l[i]
        return ans


Horner.horner_inv = Horner.hornerInv  # type: ignore[attr-defined]
Horner.reverse_array = Horner.reverseArray  # type: ignore[attr-defined]
Horner.left_right_reverse = Horner.leftRightReverse  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# ArrayString
# ---------------------------------------------------------------------------


def _array_string_to_string(arr: Any) -> str:
    if arr is None:
        return "null"
    if isinstance(arr, (str, bytes)):
        return str(arr)
    if isinstance(arr, bool):
        return "true" if arr else "false"
    is_array = isinstance(arr, (list, tuple))
    if not is_array:
        to_s = getattr(arr, "toString", None)
        if callable(to_s):
            try:
                return str(to_s())
            except TypeError:
                pass
        return str(arr)
    parts = [_array_string_to_string(arr[i]) for i in range(len(arr))]
    return "[" + ",".join(parts) + "]"


class ArrayString(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def toString(arr):
        return _array_string_to_string(arr)

    @staticmethod
    def to_string(arr):
        return _array_string_to_string(arr)


# ---------------------------------------------------------------------------
# ArrayIncrementor protocol name
# ---------------------------------------------------------------------------


class ArrayIncrementor(object):
    """Java interface name; incrementors implement ``increment()``."""

    def increment(self) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# PermutationGenerator (Johnson-Trotter, matching Java)
# ---------------------------------------------------------------------------


class PermutationGenerator(object):
    def __init__(self, n: int) -> None:
        self.n = int(n)
        if self.n < 1:
            raise IllegalArgumentException("Min 1")
        self.a = list(range(self.n))
        self.arrows = [False] * self.n
        self.largestMobileIndex = -1
        self.reset()

    def reset(self) -> None:
        self.arrows = [False] * self.n
        self.a = list(range(self.n))

    def _find_largest_mobile_index(self) -> int:
        largest_mob = -1
        largest_mobile_ind = -1
        n = self.n
        a = self.a
        arrows = self.arrows
        for i in range(n):
            if a[i] > largest_mob:
                if arrows[a[i]]:
                    if i != n - 1 and a[i] > a[i + 1]:
                        largest_mobile_ind = i
                        largest_mob = a[i]
                else:
                    if i != 0 and a[i] > a[i - 1]:
                        largest_mobile_ind = i
                        largest_mob = a[i]
        return largest_mobile_ind

    def nextIndex(self) -> int:
        k = self.largestMobileIndex
        if k == -1:
            k = self._find_largest_mobile_index()
        if k == -1:
            return -1
        if self.arrows[self.a[k]]:
            ans = k
        else:
            ans = k - 1
        for i in range(self.a[k] + 1, self.n):
            self.arrows[i] = not self.arrows[i]
        tmp = self.a[ans]
        self.a[ans] = self.a[ans + 1]
        self.a[ans + 1] = tmp
        self.largestMobileIndex = -1
        return ans

    def next_index(self) -> int:
        return self.nextIndex()

    @staticmethod
    def iterator(n):
        g = PermutationGenerator(int(n))
        first = [True]

        class _It(object):
            def hasNext(self):
                g.largestMobileIndex = g._find_largest_mobile_index()
                return g.largestMobileIndex != -1

            def next(self):
                if first[0]:
                    first[0] = False
                    return g.a
                if g.nextIndex() == -1:
                    raise StopIteration()
                return g.a

            def has_next(self):
                return self.hasNext()

            def __iter__(self):
                return self

            def __next__(self):
                if not first[0] and not self.hasNext() and g.largestMobileIndex == -1:
                    # after first, hasNext already updated largestMobileIndex
                    pass
                if first[0]:
                    # Python iteration: yield identity first without requiring hasNext
                    first[0] = False
                    return list(g.a)
                idx = g.nextIndex()
                if idx == -1:
                    raise StopIteration()
                return list(g.a)

        return _It()

    @staticmethod
    def arrayIncrementor(arr):
        g = PermutationGenerator(len(arr))

        def swap(k: int) -> None:
            tmp = arr[k]
            arr[k] = arr[k + 1]
            arr[k + 1] = tmp

        def increment() -> bool:
            while True:
                k = g.nextIndex()
                if k == -1:
                    if len(arr) > 1:
                        swap(0)
                    return False
                if arr[k] == arr[k + 1]:
                    continue
                swap(k)
                return True

        return _InPlaceIncrementor(increment)

    @staticmethod
    def listIncrementor(lst):
        g = PermutationGenerator(len(lst))

        def swap(k: int) -> None:
            tmp = lst[k]
            lst[k] = lst[k + 1]
            lst[k + 1] = tmp

        def increment() -> bool:
            while True:
                k = g.nextIndex()
                if k == -1:
                    if len(lst) > 1:
                        swap(0)
                    return False
                if lst[k] == lst[k + 1]:
                    continue
                swap(k)
                return True

        return _InPlaceIncrementor(increment)


PermutationGenerator.array_incrementor = PermutationGenerator.arrayIncrementor  # type: ignore[attr-defined]
PermutationGenerator.list_incrementor = PermutationGenerator.listIncrementor  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# IntArray helpers
# ---------------------------------------------------------------------------


class _NullIntArray(object):
    """Java ``IntArray()``: array is null, size is -1."""

    def universeSize(self) -> int:
        return -1

    def universe_size(self) -> int:
        return -1

    def getArray(self) -> None:
        return None

    def toArray(self) -> None:
        return None

    def to_array(self) -> None:
        return None

    def get(self, _i: int) -> int:
        raise NullPointerException()

    def set(self, _i: int, _v: int) -> None:
        raise NullPointerException()

    def setIntArray(self, v: Any) -> None:
        raise TypeError("null IntArray cannot replace its array via this sentinel")

    def clone(self) -> Any:
        return _NullIntArray()

    def clone_array(self) -> Any:
        return self.clone()

    def isIdempotent(self) -> bool:
        raise NullPointerException()

    def isConstant(self) -> bool:
        raise NullPointerException()

    def toString(self) -> str:
        raise NullPointerException()

    def __str__(self) -> str:
        raise NullPointerException()

    def hashCode(self) -> int:
        raise NullPointerException()

    def __hash__(self) -> int:
        raise NullPointerException()

    def equals(self, obj: Any) -> bool:
        if obj is None:
            return False
        raise NullPointerException()

    def __eq__(self, other: Any) -> bool:
        return False if other is None else (other is self)


def _install_int_array(g: dict) -> None:
    Lib = g.get("_LibIntArray") or g.get("IntArray")
    if Lib is None:
        return

    def _vals(self: Any) -> List[int]:
        getter = getattr(self, "to_array", None) or getattr(self, "getArray", None)
        if callable(getter):
            return [int(x) for x in getter()]
        return []

    def universeSize(self: Any) -> int:
        return int(self.universe_size() if hasattr(self, "universe_size") else self.universeSize())

    def getArray(self: Any) -> List[int]:
        return _vals(self)

    def toArray(self: Any) -> List[int]:
        return _vals(self)

    def setIntArray(self: Any, v: Any) -> None:
        values = _as_int_list(v)
        # Same-length write through set(); length change is a library gap.
        if int(self.universeSize()) != len(values):
            raise UnsupportedOperationException(
                "IntArray.setIntArray cannot replace the backing store (uacalc_lib)"
            )
        for i, val in enumerate(values):
            self.set(i, int(val))

    def clone(self: Any) -> Any:
        fn = getattr(self, "clone_array", None) or getattr(self, "clone", None)
        return fn() if callable(fn) else self

    def toString(self: Any) -> str:
        return intArrayToString(_vals(self))

    def hashCode(self: Any) -> int:
        return _java_hash_code(_vals(self))

    def equals(self: Any, obj: Any) -> bool:
        if obj is None:
            return False
        other = getattr(obj, "getArray", None) or getattr(obj, "to_array", None)
        if not callable(other):
            return False
        try:
            return equalIntArrays(_vals(self), list(other()))
        except Exception:
            return False

    def isIdempotent(self: Any) -> bool:
        fn = getattr(self, "is_idempotent", None)
        return bool(fn()) if callable(fn) else False

    def isConstant(self: Any) -> bool:
        fn = getattr(self, "is_constant", None)
        return bool(fn()) if callable(fn) else False

    def satisfiesBlocksConstraint(self: Any, blocks: Any) -> bool:
        fn = getattr(self, "satisfies_blocks_constraint", None)
        if callable(fn):
            return bool(fn(blocks))
        return False

    def satisfiesValuesConstraint(self: Any, values: Any) -> bool:
        fn = getattr(self, "satisfies_values_constraint", None)
        if callable(fn):
            pairs = []
            for pair in values:
                pairs.append((int(pair[0]), int(pair[1])))
            try:
                return bool(fn(pairs))
            except TypeError:
                return bool(fn(values))
        return False

    def satisfiesSetConstraint(self: Any, index: int, possibleValues: Any) -> bool:
        fn = getattr(self, "satisfies_set_constraint", None)
        if callable(fn):
            return bool(fn(int(index), set(int(x) for x in possibleValues)))
        return int(self.get(int(index))) in set(int(x) for x in possibleValues)

    def satisfiesCongruenceConstraint(self: Any, index: int, alpha: Any, elemIndex: int) -> bool:
        related = getattr(alpha, "isRelated", None) or getattr(alpha, "is_related", None)
        if not callable(related):
            raise IllegalArgumentException("Partition constraint requires isRelated")
        return bool(related(int(elemIndex), int(self.get(int(index)))))

    def intArrayToString(array: Any) -> str:
        if array is None:
            raise NullPointerException()
        values = _as_int_list(array)
        if not values:
            return "[]"
        return "[" + ", ".join(str(int(x)) for x in values) + "]"

    def stringToArray(s: Any) -> List[int]:
        if s is None:
            raise NullPointerException()
        s = str(s).strip()
        if not s:
            raise IllegalArgumentException("For input string: \"\"")
        import re

        elts = [p for p in re.split(r"[,\s]+", s) if p]
        try:
            return [int(x) for x in elts]
        except ValueError as exc:
            from org.uacalc._exceptions import NumberFormatException

            raise NumberFormatException(str(exc)) from exc

    def equalIntArrays(u: Any, v: Any) -> bool:
        if u is None or v is None:
            raise NullPointerException()
        uu = _as_int_list(u)
        vv = _as_int_list(v)
        return uu == vv

    def lexicographicComparitor() -> _LexComparator:
        return _LexComparator()

    _bind(Lib, "universeSize", universeSize)
    _bind(Lib, "getArray", getArray)
    _bind(Lib, "toArray", toArray)
    _bind(Lib, "setIntArray", setIntArray)
    _bind(Lib, "clone", clone)
    _bind(Lib, "toString", toString)
    _bind(Lib, "hashCode", hashCode)
    _bind(Lib, "equals", equals)
    _bind(Lib, "isIdempotent", isIdempotent)
    _bind(Lib, "isConstant", isConstant)
    _bind(Lib, "satisfiesBlocksConstraint", satisfiesBlocksConstraint)
    _bind(Lib, "satisfiesValuesConstraint", satisfiesValuesConstraint)
    _bind(Lib, "satisfiesSetConstraint", satisfiesSetConstraint)
    _bind(Lib, "satisfiesCongruenceConstraint", satisfiesCongruenceConstraint)
    _bind(Lib, "intArrayToString", staticmethod(intArrayToString))
    _bind(Lib, "stringToArray", staticmethod(stringToArray))
    _bind(Lib, "equalIntArrays", staticmethod(equalIntArrays))
    _bind(Lib, "lexicographicComparitor", staticmethod(lexicographicComparitor))

    class _IntArrayMeta(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, Lib) or isinstance(instance, _NullIntArray)

    class IntArray(object, metaclass=_IntArrayMeta):  # noqa: N801
        def __new__(cls, *args):
            if len(args) == 0:
                return _NullIntArray()
            if len(args) != 1:
                raise TypeError("IntArray() takes 0 or 1 arguments")
            arg = args[0]
            if isinstance(arg, (list, tuple)):
                return Lib.from_array([int(x) for x in arg])
            if isinstance(arg, _NullIntArray):
                return arg
            if isinstance(arg, Lib):
                return arg
            return Lib(int(arg))

    IntArray.from_array = staticmethod(Lib.from_array)
    IntArray.intArrayToString = staticmethod(intArrayToString)
    IntArray.stringToArray = staticmethod(stringToArray)
    IntArray.equalIntArrays = staticmethod(equalIntArrays)
    IntArray.lexicographicComparitor = staticmethod(lexicographicComparitor)

    g["IntArray"] = IntArray
    g["_LibIntArray"] = Lib
    g["_NullIntArray"] = _NullIntArray


# ---------------------------------------------------------------------------
# SimpleList Java names
# ---------------------------------------------------------------------------


def _install_simple_list(g: dict) -> None:
    Lib = g.get("SimpleList")
    if Lib is None:
        return

    def _empty() -> Any:
        return Lib()

    empty = _empty()

    def makeList(obj: Any = None) -> Any:
        if obj is None:
            return _empty()
        return _empty().cons(obj)

    def isEmpty(self: Any) -> bool:
        fn = getattr(self, "is_empty", None)
        return bool(fn()) if callable(fn) else False

    def copyList(self: Any) -> Any:
        fn = getattr(self, "copy_list", None)
        return fn() if callable(fn) else self

    def indexOf(self: Any, obj: Any) -> int:
        fn = getattr(self, "index_of", None)
        if callable(fn):
            idx = fn(obj)
            return -1 if idx is None else int(idx)
        return -1

    def lastIndexOf(self: Any, obj: Any) -> int:
        fn = getattr(self, "last_index_of", None)
        if callable(fn):
            idx = fn(obj)
            return -1 if idx is None else int(idx)
        return -1

    def containsAll(self: Any, c: Any) -> bool:
        fn = getattr(self, "contains_all", None)
        if callable(fn) and type(c).__name__.endswith("SimpleList"):
            return bool(fn(c))
        for item in c:
            if not self.contains(item):
                return False
        return True

    def subList(self: Any, i: int, j: int) -> Any:
        fn = getattr(self, "sub_list", None)
        if callable(fn):
            return fn(int(i), int(j))
        raise IndexOutOfBoundsException()

    def toArray(self: Any, a: Any = None) -> List[Any]:
        fn = getattr(self, "to_list", None)
        items = list(fn()) if callable(fn) else list(self)
        if a is None:
            return items
        raise UnsupportedOperationException()

    def toString(self: Any) -> str:
        parts = []
        cur = self
        while True:
            empty_fn = getattr(cur, "isEmpty", None) or getattr(cur, "is_empty", None)
            if callable(empty_fn) and empty_fn():
                break
            first_fn = getattr(cur, "first", None)
            rest_fn = getattr(cur, "rest", None)
            if not callable(first_fn) or not callable(rest_fn):
                break
            parts.append(str(first_fn()))
            cur = rest_fn()
        return "(" + " ".join(parts) + ")"

    def add(self: Any, *args: Any) -> None:
        raise UnsupportedOperationException()

    def addAll(self: Any, *args: Any) -> None:
        raise UnsupportedOperationException()

    def clear(self: Any) -> None:
        raise UnsupportedOperationException()

    def remove(self: Any, *args: Any) -> None:
        raise UnsupportedOperationException()

    def removeAll(self: Any, *args: Any) -> None:
        raise UnsupportedOperationException()

    def retainAll(self: Any, *args: Any) -> None:
        raise UnsupportedOperationException()

    def set_uoe(self: Any, *args: Any) -> None:
        raise UnsupportedOperationException()

    def listIterator(self: Any, *args: Any) -> None:
        raise UnsupportedOperationException()

    def elements(self: Any) -> Any:
        return iter(self)

    def getIterator(self: Any) -> Any:
        return iter(self)

    def frontIterator(self: Any, tail: Any) -> Any:
        items = []
        cur = self
        while True:
            empty_fn = getattr(cur, "isEmpty", None) or getattr(cur, "is_empty", None)
            if callable(empty_fn) and empty_fn():
                break
            if cur is tail:
                break
            first_fn = getattr(cur, "first", None)
            rest_fn = getattr(cur, "rest", None)
            if not callable(first_fn):
                break
            items.append(first_fn())
            cur = rest_fn() if callable(rest_fn) else None
            if cur is None:
                break
        return iter(items)

    def reverse_java(self: Any, lst: Any = None) -> Any:
        if lst is None:
            fn = getattr(self, "reverse", None)
            return fn() if callable(fn) else self
        fn = getattr(self, "reverse_with", None)
        if callable(fn):
            return fn(lst)
        return self.reverse().append(lst)

    def app(self: Any, other: Any) -> Any:
        return self.append(other)

    def rev(self: Any) -> Any:
        return self.reverse()

    _bind(Lib, "makeList", staticmethod(makeList))
    _bind(Lib, "isEmpty", isEmpty)
    _bind(Lib, "copyList", copyList)
    _bind(Lib, "indexOf", indexOf)
    _bind(Lib, "lastIndexOf", lastIndexOf)
    _bind(Lib, "containsAll", containsAll)
    _bind(Lib, "subList", subList)
    _bind(Lib, "toArray", toArray)
    _bind(Lib, "toString", toString)
    _bind(Lib, "add", add)
    _bind(Lib, "addAll", addAll)
    _bind(Lib, "clear", clear)
    _bind(Lib, "remove", remove)
    _bind(Lib, "removeAll", removeAll)
    _bind(Lib, "retainAll", retainAll)
    _bind(Lib, "listIterator", listIterator)
    _bind(Lib, "elements", elements)
    _bind(Lib, "getIterator", getIterator)
    _bind(Lib, "frontIterator", frontIterator)
    _bind(Lib, "app", app)
    _bind(Lib, "rev", rev)
    # Keep Lib.set (index set) if present; List.set throws in Java for some overloads.
    _bind(Lib, "EMPTY_LIST", empty)
    _bind(Lib, "emptyList", empty)

    _Lib = Lib

    class _SimpleListMeta(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, _Lib)

    class SimpleList(object, metaclass=_SimpleListMeta):  # noqa: N801
        def __new__(cls, *args):
            if len(args) == 0:
                return _empty()
            if len(args) == 1:
                c = args[0]
                if hasattr(c, "__iter__") and not isinstance(c, (str, bytes)):
                    from_list = getattr(_Lib, "from_list", None)
                    if callable(from_list):
                        return from_list(list(c))
                return makeList(c)
            if len(args) == 2:
                obj, rest = args
                if hasattr(rest, "cons"):
                    return rest.cons(obj)
                return makeList(obj)
            raise TypeError("SimpleList() takes 0, 1, or 2 arguments")

    SimpleList.EMPTY_LIST = empty
    SimpleList.emptyList = empty
    SimpleList.makeList = staticmethod(makeList)

    g["SimpleList"] = SimpleList
    g["_LibSimpleList"] = _Lib


def _install(g: dict) -> None:
    g["SequenceGenerator"] = SequenceGenerator
    g["Horner"] = Horner
    g["ArrayString"] = ArrayString
    g["ArrayIncrementor"] = ArrayIncrementor
    g["PermutationGenerator"] = PermutationGenerator
    g["_InPlaceIncrementor"] = _InPlaceIncrementor
    _install_int_array(g)
    _install_simple_list(g)
    # Drop unused import warning
    _ = translate_illegal_argument
    _ = Iterable
    _ = Optional
