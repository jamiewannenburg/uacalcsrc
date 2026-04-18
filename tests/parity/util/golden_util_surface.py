#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.util``.

Runs under **CPython** (shim → ``uacalc_lib.util``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython** (repo root)::

    PYTHONPATH=python python tests/parity/util/golden_util_surface.py

**Windows (PowerShell)**::

    $env:PYTHONPATH = "python"; python tests/parity/util/golden_util_surface.py

**Jython** (Java on classpath; do not put ``python/`` on ``PYTHONPATH`` so the
real Java package is used)::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/util/golden_util_surface.py

Jython's ``org.uacalc.util`` package does not populate ``dir()`` until concrete
types are imported; the script imports the public Java classes first so the
listing matches what callers see after those imports. The ``virtuallist``
subpackage is imported so it appears in ``dir()`` like typical script usage.
"""
from __future__ import print_function

import sys


def main():
    if sys.platform.startswith('java'):
        from org.uacalc.util import ArrayIncrementor  # noqa: F401
        from org.uacalc.util import ArrayString  # noqa: F401
        from org.uacalc.util import Horner  # noqa: F401
        from org.uacalc.util import IntArray  # noqa: F401
        from org.uacalc.util import PermutationGenerator  # noqa: F401
        from org.uacalc.util import SequenceGenerator  # noqa: F401
        from org.uacalc.util import SimpleList  # noqa: F401
        import org.uacalc.util.virtuallist  # noqa: F401

    else:
        import org.uacalc.util.virtuallist  # noqa: F401

    import org.uacalc.util as util_pkg

    is_java = sys.platform.startswith('java')
    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.util')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(util_pkg) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    print('HAS_VIRTUAL_LIST: ' + ('yes' if 'virtuallist' in names else 'no'))
    for n in names:
        print('NAME: ' + n)


if __name__ == '__main__':
    main()
