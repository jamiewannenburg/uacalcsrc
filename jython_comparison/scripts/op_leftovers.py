# coding: utf-8
# Dual-runtime parity script for leftover org.uacalc.alg.op types.
from __future__ import print_function

from org.uacalc.alg.op import (
    AbstractIntOperation,
    OperationSymbol,
    OperationWithDefaultValue,
    Operations,
    ParameterizedOperation,
    TermOperationImp,
)
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import NonVariableTerm, VariableImp


def test():
    aio = AbstractIntOperation(OperationSymbol("*", 2), 3)
    print("aio_size=" + str(aio.getSetSize()))
    try:
        aio.valueAt([0, 1])
        print("aio_va=ok")
    except Exception:
        import sys
        print("aio_va=" + type(sys.exc_info()[1]).__name__)
    except:
        import sys
        print("aio_va=" + type(sys.exc_info()[1]).__name__)
    try:
        aio.intValueAt([0, 1])
        print("aio_iva=ok")
    except Exception:
        import sys
        print("aio_iva=" + type(sys.exc_info()[1]).__name__)
    except:
        import sys
        print("aio_iva=" + type(sys.exc_info()[1]).__name__)

    c2 = AlgebraIO.readAlgebraFile("resources/algebras/cyclic2.ua")
    plus = OperationSymbol("+", 2)
    x = VariableImp("x")
    y = VariableImp("y")
    try:
        from java.util import ArrayList
        vars_xy = ArrayList()
        vars_xy.add(x)
        vars_xy.add(y)
    except ImportError:
        vars_xy = [x, y]
    term = NonVariableTerm(plus, vars_xy)
    toi = TermOperationImp(term, vars_xy, c2)
    print("toi_term=" + str(toi.getTerm()).replace(" ", ""))
    print("toi_vars=" + str([str(v) for v in list(toi.getOrderedVariables())]))
    print("toi_iva=" + str(toi.intValueAt([1, 0])))
    print("toi_va=" + str(toi.valueAt([1, 1])))
    try:
        tab = toi.getTable()
        print("toi_table=" + str(None if tab is None else [int(x) for x in list(tab)]))
    except Exception:
        import sys
        print("toi_table=" + type(sys.exc_info()[1]).__name__)
    except:
        import sys
        print("toi_table=" + type(sys.exc_info()[1]).__name__)
    tab_t = toi.getTable(True)
    print("toi_table_true=" + str(None if tab_t is None else [int(x) for x in list(tab_t)]))
    print("toi_str=" + toi.toString().replace(" ", ""))

    def _set_parm(obj, name, value):
        try:
            f = obj.getClass().getDeclaredField(name)
            f.setAccessible(True)
            f.set(obj, value)
            return
        except Exception:
            pass
        setattr(obj, name, value)

    parm = ParameterizedOperation()
    _set_parm(parm, "symbolName", "m")
    _set_parm(parm, "arityExp", "2")
    _set_parm(parm, "setSizeExp", "3")
    _set_parm(parm, "definitionExp", "x")
    print("parm_sub=" + ParameterizedOperation.subParmValues("n+1", {"n": "3"}))
    mop = parm.makeOp({"n": "1"})
    print("parm_max=" + str(mop.intValueAt([1, 2])))

    ow = OperationWithDefaultValue(OperationSymbol("f", 2), 2, 7)
    print("ow_def=" + str(ow.getDefaultValue()))
    print("ow_size=" + str(ow.getSetSize()))
    print("ow_total=" + str(ow.isTotal()))
    print("ow_iva=" + str(ow.intValueAt([0, 1])))
    print("ow_va=" + str(ow.valueAt([1, 0])))
    print("ow_tab=" + str(ow.getTable()))
    ow.setDefaultValue(1)
    print("ow_set=" + str(ow.getDefaultValue()))
    print("ow_totaltab=" + str(ow.getTotalTable()))
    ordop = ow.makeOrdinaryOperation()
    print("ow_ord=" + str(ordop.intValueAt([0, 0])))
    ow.makeTable()
    print("ow_made=" + str(ow.getTable() is not None))
    ow2 = OperationWithDefaultValue("h", 2, 3, -1)
    print("ow2_idemset=" + str(ow2.isIdempotentSet()))
    ow2.setIdempotent(True)
    print("ow2_idemset2=" + str(ow2.isIdempotentSet()))
    ow2.makeIdempotent()
    print("ow2_diag=" + str(ow2.isDiagonal(0, 0)))
    xor = Operations.makeIntOperation(OperationSymbol("xor", 2), 2, [0, 1, 1, 0])
    owx = OperationWithDefaultValue(xor)
    print("owx_iva=" + str(owx.intValueAt([1, 0])))
    print("ow_ordlist=" + str(len(OperationWithDefaultValue.makeOrdinary([owx]))))
    ow2.updateRandomValueTable()
    rtab = ow2.getRandomValueTable()
    print("ow_randlen=" + str(len(rtab)))


if __name__ == "__main__":
    test()
