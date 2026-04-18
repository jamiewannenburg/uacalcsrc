#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden surface snapshot for ``org.uacalc.group``.

Runs under **CPython** (shim → ``uacalc_lib.group``) and **Jython** (Java
classes from ``uacalc.jar``). Normalized stdout is compared to checked-in
fixtures by pytest.

**CPython**::

    PYTHONPATH=python python tests/parity/group/golden_group_surface.py

**Jython**::

    CLASSPATH=jars/uacalc.jar PYTHONPATH= jython tests/parity/group/golden_group_surface.py

Imports ``PermutationGroup`` first so ``dir()`` lists the type.
"""
from __future__ import print_function

import sys


def main():
    from org.uacalc.group import PermutationGroup  # noqa: F401

    import org.uacalc.group as group_pkg

    is_java = sys.platform.startswith('java')
    runtime = 'jython' if is_java else 'cpython'

    print('MODULE: org.uacalc.group')
    print('RUNTIME: ' + runtime)
    names = sorted(n for n in dir(group_pkg) if not n.startswith('_'))
    print('PUBLIC_COUNT: ' + str(len(names)))
    print('HAS_PERMUTATION_GROUP: ' + (
        'yes' if 'PermutationGroup' in names else 'no'))
    for n in names:
        print('NAME: ' + n)

    g = PermutationGroup('S2', [(0, 1)])
    # Java default __str__ is unstable (object id); Rust/Python use a readable repr.
    if is_java:
        print('SMOKE_S2_NAME: ' + str(g.getName()))
    else:
        print('SMOKE_S2_NAME: ' + str(g.get_name()))


if __name__ == '__main__':
    main()
