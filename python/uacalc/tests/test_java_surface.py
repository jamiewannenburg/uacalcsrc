"""Unit tests for the Java public-surface scanner."""

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from jython_contracts.java_surface import (  # noqa: E402
    ANONYMOUS_INNER_CLASS,
    COMMENTED_OUT,
    GUI,
    LEGACY,
    MAIN,
    NON_PUBLIC_TYPE,
    scan_java_file,
    scan_java_source,
)


def _by_name(surface):
    return {t.simple_name: t for t in surface.types}


def _excluded(typ, category):
    return {m.name for m in typ.members if m.exclusion == category}


def _live(typ):
    return set(typ.public_surface)


def test_anonymous_inner_class_methods_are_excluded():
    src = """
package org.uacalc.lat;
public class BasicLattice {
  public int cardinality() { return 0; }
  private Operation makeJoin() {
    return new AbstractOperation("join", n) {
        public Object valueAt(List args) { return args; }
        public int intValueAt(int[] args) { return 0; }
    };
  }
}
"""
    types = _by_name(scan_java_source(src))
    lat = types["BasicLattice"]
    assert "cardinality" in _live(lat)
    assert _excluded(lat, ANONYMOUS_INNER_CLASS) >= {"valueAt", "intValueAt"}
    assert "valueAt" not in _live(lat)
    assert "intValueAt" not in _live(lat)


def test_commented_out_public_methods_are_excluded():
    src = """
package org.uacalc.alg;
public class BigProductAlgebra {
  public List sgClose(List elems) { return elems; }
  /*
  public Subalgebra sg(List elems) {
    return null;
  }
  */
}
"""
    types = _by_name(scan_java_source(src))
    bpa = types["BigProductAlgebra"]
    assert "sgClose" in _live(bpa)
    assert "sg" in _excluded(bpa, COMMENTED_OUT)
    assert "sg" not in _live(bpa)


def test_main_is_excluded_constructor_is_surface():
    src = """
package org.uacalc.alg.conlat;
public class Polymorphisms {
  public Polymorphisms(int arity, List pars, boolean idempotent, int[] fixed) {}
  public static void main(String[] args) {}
}
"""
    types = _by_name(scan_java_source(src))
    poly = types["Polymorphisms"]
    assert "Polymorphisms" in _live(poly)
    assert "main" in _excluded(poly, MAIN)
    assert "main" not in _live(poly)


def test_legacy_old_and_xx_overloads():
    src = """
package org.uacalc.alg;
public class BigProductAlgebra {
  public List sgClose(List elems) { return elems; }
  public List sgClose_old(List elems, int closedMark) { return elems; }
  public List sgCloseXX(List elems, int closedMark) { return elems; }
  public Partition Cg_Old(Partition part) { return part; }
}
"""
    types = _by_name(scan_java_source(src))
    bpa = types["BigProductAlgebra"]
    assert "sgClose" in _live(bpa)
    assert _excluded(bpa, LEGACY) >= {"sgClose_old", "sgCloseXX", "Cg_Old"}
    # Live wrapped API that happens to end in Old is not legacy.
    src2 = """
package org.uacalc.util;
public class SequenceGenerator {
  public static ArrayIncrementor increasingSequenceIncrementorOld(int[] a, int max) {
    return null;
  }
}
"""
    seq = _by_name(scan_java_source(src2))["SequenceGenerator"]
    assert "increasingSequenceIncrementorOld" in _live(seq)


def test_gui_inner_class_and_nested_enum_isolation():
    src = """
package org.uacalc.alg.conlat;
public class Partition {
  public boolean isRelated(int i, int j);
  public enum PrintType { INTERNAL, EWK }
  private static class FrameShower implements Runnable {
    public void run() {}
  }
}
"""
    types = _by_name(scan_java_source(src))
    part = types["Partition"]
    assert "isRelated" in _live(part)
    assert "run" not in _live(part)
    print_type = types["PrintType"]
    assert "isRelated" not in _live(print_type)
    shower = types["FrameShower"]
    assert "run" in _excluded(shower, GUI) or "run" in _excluded(shower, NON_PUBLIC_TYPE)


def test_package_private_not_on_surface():
    src = """
package org.uacalc.alg.parallel;
public class Pool {
  static ForkJoinPool fjPool;
  public static boolean isInitialized() { return true; }
  void helper() {}
}
"""
    types = _by_name(scan_java_source(src))
    pool = types["Pool"]
    assert "isInitialized" in _live(pool)
    assert "helper" not in _live(pool)


def test_real_polymorphisms_file():
    path = REPO_ROOT / "org/uacalc/alg/conlat/Polymorphisms.java"
    poly = _by_name(scan_java_file(path))["Polymorphisms"]
    assert poly.public_constructors == ["Polymorphisms"]
    assert "main" in _excluded(poly, MAIN)
    assert poly.public_methods == []


def test_real_basic_lattice_anonymous_and_gui():
    path = REPO_ROOT / "org/uacalc/lat/BasicLattice.java"
    lat = _by_name(scan_java_file(path))["BasicLattice"]
    live = _live(lat)
    assert "cardinality" in live or "getPoset" in live
    assert "valueAt" not in live
    assert "intValueAt" not in live
    assert "main" not in live
    assert "run" not in live


def test_real_big_product_algebra_commented_sg_and_legacy():
    path = REPO_ROOT / "org/uacalc/alg/BigProductAlgebra.java"
    bpa = _by_name(scan_java_file(path))["BigProductAlgebra"]
    live = _live(bpa)
    assert "sgClose" in live
    assert "sg" not in live
    assert "sg" in _excluded(bpa, COMMENTED_OUT)
    assert _excluded(bpa, LEGACY) >= {"sgClose_old", "sgCloseXX"}
    assert "main" not in live


def test_real_partition_print_type_does_not_inherit_methods():
    path = REPO_ROOT / "org/uacalc/alg/conlat/Partition.java"
    types = _by_name(scan_java_file(path))
    assert "isRelated" in _live(types["Partition"])
    assert "isRelated" not in _live(types["PrintType"])


def test_real_subalgebra_lattice_commented_task():
    path = REPO_ROOT / "org/uacalc/alg/sublat/SubalgebraLattice.java"
    sub = _by_name(scan_java_file(path))["SubalgebraLattice"]
    assert "getUniverseTask" in _excluded(sub, COMMENTED_OUT)
    assert "percentDone" in _excluded(sub, COMMENTED_OUT) or "percentDone" in _excluded(
        sub, ANONYMOUS_INNER_CLASS
    )
    assert "getUniverseTask" not in _live(sub)


def test_real_int_array_commented_constraint():
    path = REPO_ROOT / "org/uacalc/util/IntArray.java"
    ia = _by_name(scan_java_file(path))["IntArray"]
    assert "satisfiesConstraint" in _excluded(ia, COMMENTED_OUT)
    assert "satisfiesConstraint" not in _live(ia)


def test_ext_file_filter_is_library_surface_not_gui():
    """ExtFileFilter extends FileFilter; that is IO API, not a Swing widget."""
    src = """
package org.uacalc.io;
public class ExtFileFilter extends javax.swing.filechooser.FileFilter {
  public ExtFileFilter(String desc, String ext) {}
  public boolean accept(File f) { return true; }
  public String getDescription() { return ""; }
  public static String getExtension(File f) { return ""; }
  public static void main(String[] args) {}
}
"""
    types = _by_name(scan_java_source(src))
    live = _live(types["ExtFileFilter"])
    assert {"ExtFileFilter", "accept", "getDescription", "getExtension"} <= live
    assert "main" not in live
    assert "main" in _excluded(types["ExtFileFilter"], MAIN)

    path = REPO_ROOT / "org/uacalc/io/ExtFileFilter.java"
    real = _by_name(scan_java_file(path))["ExtFileFilter"]
    real_live = _live(real)
    assert "accept" in real_live
    assert "getDescription" in real_live
    assert "ExtFileFilter" in real_live
    assert "main" not in real_live


def test_jdialog_subclass_outside_ui_package_is_gui():
    src = """
package org.uacalc.alg;
public class NewAlgebraDialog extends JDialog {
  public void showIt() {}
}
"""
    types = _by_name(scan_java_source(src))
    assert "showIt" in _excluded(types["NewAlgebraDialog"], GUI)
    assert "showIt" not in _live(types["NewAlgebraDialog"])
