# coding: utf-8
# Dual-runtime parity script for Operation / Operations / SimilarityType.
from __future__ import print_function

from org.uacalc.alg.op import Operations, OperationSymbol, SimilarityType


def _op(name, arity, size, table):
    return Operations.makeIntOperation(OperationSymbol(name, arity), size, table)


def test():
    xor2 = _op("xor", 2, 2, [0, 1, 1, 0])
    and2 = _op("and", 2, 2, [0, 0, 0, 1])
    print("arity=" + str(xor2.arity()))
    print("setSize=" + str(xor2.getSetSize()))
    print("valueAt=" + str(xor2.valueAt([1, 0])))
    print("intValueAt=" + str(xor2.intValueAt([1, 1])))
    xor2.makeTable()
    print("table=" + str(list(xor2.getTable())))
    print("table2=" + str(list(xor2.getTable(True))))
    print("tableBased=" + str(xor2.isTableBased()))
    print("idem=" + str(xor2.isIdempotent()) + "/" + str(and2.isIdempotent()))
    print("assoc=" + str(xor2.isAssociative()))
    print("comm=" + str(xor2.isCommutative()))
    print("tsym=" + str(xor2.isTotallySymmetric()))
    print("maltsev=" + str(xor2.isMaltsev()))
    print("total=" + str(xor2.isTotal()))

    id1 = Operations.makeIntOperation("id", 1, 2, [0, 1])
    print("commutes=" + str(Operations.commutes(id1, xor2)))
    print("ops_total=" + str(Operations.isTotal(xor2)))
    print("ops_idem=" + str(Operations.isIdempotent(and2)))
    print("ops_comm=" + str(Operations.isCommutative(xor2)))
    print("ops_tsym=" + str(Operations.isTotallySymmetric(and2)))
    print("ops_assoc=" + str(Operations.isAssociative(xor2)))
    print("ops_maltsev=" + str(Operations.isMaltsev(xor2)))
    print("diff_none=" + str(Operations.findDifference(xor2, xor2)))
    print("eq_vals=" + str(Operations.equalValues(xor2, xor2)))
    mm = Operations.makeMap([xor2, and2])
    if hasattr(mm, "keySet"):
        keys = sorted(str(k) for k in mm.keySet())
    else:
        keys = sorted(str(k) for k in mm)
    print("map_keys=" + str(keys))
    print("from_op=" + str(Operations.makeIntOperation(xor2).arity()))
    print("int_ops=" + str(len(Operations.makeIntOperations([xor2]))))
    print(
        "bin="
        + str(
            Operations.makeBinaryIntOperation(
                OperationSymbol("b", 2), 2, [[0, 1], [1, 0]]
            ).intValueAt([1, 0])
        )
    )
    print("const=" + str(Operations.makeConstantIntOperation(3, 1).intValueAt([])))
    print("const_n=" + str(len(Operations.makeConstantIntOperations(2))))
    print("trans=" + str(Operations.makeTransposition(3, 0, 2).intValueAt([0])))
    print("cycle=" + str(Operations.makeFullCycle(3).intValueAt([2])))
    print("disc=" + str(Operations.ternaryDiscriminator(2).arity()))
    print("rand=" + str(Operations.makeRandomOperation(2, OperationSymbol("r", 1)).arity()))
    st = SimilarityType([OperationSymbol("join", 2), OperationSymbol("meet", 2)])
    print("rand_n=" + str(len(Operations.makeRandomOperations(2, st, 1))))
    print("derived=" + str(Operations.makeDerivedOperation(xor2, [0, 0], 1).arity()))
    print("left=" + str(Operations.makeLeftShift(2, 2).getSetSize()))
    print("bleft=" + str(Operations.makeBinaryLeftShift(2, 2).arity()))
    print("diag=" + str(Operations.makeMatrixDiagonalOp(2, 2).arity()))
    print("mod=" + str(Operations.makeModuleOperation(3, [1, 0]).intValueAt([1, 2])))
    print("comp=" + str(Operations.makeCompositionOp(2, 4).arity()))
    print("power=" + str(Operations.power(2, 3)))
    nuf3 = Operations.makeIntOperation(
        "nuf", 3, 2, [0, 0, 0, 0, 0, 0, 0, 1]
    )
    print("jonsson=" + str(len(Operations.makeJonssonOperationsFromNUF(nuf3))))

    import sys
    if sys.platform.startswith("java"):
        from java.io import ByteArrayOutputStream, PrintStream
        buf = ByteArrayOutputStream()
        out = PrintStream(buf)
        Operations.binaryOpToCSV("xor", xor2, out)
        csv = str(buf.toString()).replace("\r\n", "\n").replace("\n", "|")
    else:
        try:
            from io import StringIO
        except ImportError:
            from StringIO import StringIO
        out = StringIO()
        Operations.binaryOpToCSV("xor", xor2, out)
        csv = out.getvalue().replace("\r\n", "\n").replace("\n", "|")
    print("csv_len=" + str(len(csv)))

    print("syms=" + str([str(s) for s in st.getOperationSymbols()]))
    print("sorted=" + str([str(s) for s in st.getSortedOperationSymbols()]))
    print("input=" + str(st.inputSize(3)))
    am = st.getAritiesMap()
    if hasattr(am, "get"):
        print("arities_bin=" + str(am.get(2) if am.get(2) is not None else am[2]))
    print("max_ar=" + str(st.getMaxArity()))
    print("ar_str=" + st.aritiesString())
    print("st=" + str(st))
    payload = []
    for s in st.getOperationSymbols():
        nm = s.name() if callable(getattr(s, "name", None)) else s.name
        ar = s.arity() if callable(getattr(s, "arity", None)) else s.arity
        payload.append((str(nm), int(ar)))
    st2 = SimilarityType([OperationSymbol(n, a) for n, a in payload])
    print("rt_equals=" + str(st.equals(st2)))
    print("rt_str=" + str(st2))
    join = OperationSymbol("join", 2)
    meet = OperationSymbol("meet", 2)
    print("join_cmp=" + str(join.compareTo(meet)))


if __name__ == "__main__":
    test()
