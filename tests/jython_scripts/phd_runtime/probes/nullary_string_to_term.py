# Probe: Java Terms.stringToTerm vs nullary op syntax (run under Jython for golden).
# Harness copies unchanged; prints structured lines for stdout comparison.
from org.uacalc.io import AlgebraIO
from org.uacalc.terms import Terms, Variable, VariableImp, NonVariableTerm
from org.uacalc.alg.op import OperationSymbol
import os

try:
    from java.lang import IllegalArgumentException, NullPointerException
except ImportError:
    from org.uacalc._exceptions import IllegalArgumentException, NullPointerException

_here = os.path.dirname(os.path.abspath(__file__))
_alg = os.path.normpath(os.path.join(_here, "..", "input", "b2.ua"))
alg = AlgebraIO.readAlgebraFile(_alg)


def line(kind, s, detail):
    print("{}|{}|{}".format(kind, s, detail))


for s in ("e", "e()", "f()", "x"):
    try:
        t = Terms.stringToTerm(s)
        kind = "var" if t.isaVariable() else "term"
        line("parse_ok", s, kind + ":" + str(t))
    except IllegalArgumentException as ex:
        line("parse_fail", s, ex.getMessage())

for s in ("e", "e()"):
    try:
        t = Terms.stringToTerm(s)
        try:
            v = t.intEval(alg, {Variable.x: 0})
            line("intEval_x0", s, str(v))
        except (NullPointerException, IllegalArgumentException) as ex:
            msg = getattr(ex, "getMessage", lambda: str(ex))()
            line("intEval_x0", s, type(ex).__name__ + ":" + str(msg))
        except Exception as ex:
            line("intEval_x0", s, type(ex).__name__ + ":" + str(ex))
    except IllegalArgumentException as ex:
        line("intEval_parse", s, "IllegalArgumentException:" + ex.getMessage())

try:
    c = NonVariableTerm.makeConstantTerm(OperationSymbol("e", 0))
    v = c.intEval(alg, {Variable.x: 0})
    line("makeConstant_e", "e", str(v))
except Exception as ex:
    line("makeConstant_e", "e", type(ex).__name__ + ":" + str(ex))

try:
    vi = VariableImp("e")
    v = vi.intEval(alg, {vi: 1})
    line("var_e_assign", "e", str(v))
except Exception as ex:
    line("var_e_assign", "e", type(ex).__name__ + ":" + str(ex))