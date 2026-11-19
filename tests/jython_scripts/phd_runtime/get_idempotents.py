import sys
sys.path.append("C:/Users/Vincent/Programming/UACalc_CLI/CLI/Jars/uacalc.jar")

from org.uacalc.alg import FreeAlgebra, Subalgebra
from org.uacalc.terms import Variable
from org.uacalc.eq import Equation
from org.uacalc.io import AlgebraIO
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.util import IntArray
from dmm import to_term, make_readable
from isomorphism import check_isomorphism, is_isomorphic
import itertools

import os
in_dir = 'input'
out_dir = 'output'

# tex_file_name = os.path.join(out_dir,"idempotents.tex".format(name))

c4 = AlgebraIO.readAlgebraFile(os.path.join(in_dir,"c4.ua"))
a = AlgebraIO.readAlgebraFile(os.path.join(in_dir,"c4_weaved.ua"))
b = AlgebraIO.readAlgebraFile(os.path.join(in_dir,"s3_weaved.ua"))
rs3 = AlgebraIO.readAlgebraFile(os.path.join(in_dir,"s3_reflection.ua"))

free = FreeAlgebra(b, 1, True, True)

idempotens = []

for t in free.getTerms():
    tt = t.substitute({Variable.x:t})
    eq = Equation(tt,t)
    result1 = eq.findFailureMap(c4)
    result2 = eq.findFailureMap(a)
    result3 = eq.findFailureMap(b)
    result4 = eq.findFailureMap(rs3)
    if not result1 and not result2 and not result3 and not result4:
        ok = True
        new_univ = set([])
        for e in c4.universe():
            new_univ.add(t.eval(c4,{Variable.x:e}))
        ok = ok and (new_univ == set([0,1]))
        new_univ = set([])
        for e in a.universe():
            new_univ.add(t.eval(a,{Variable.x:e}))
        ok = ok and (new_univ == set([0,1,2,3,4]))
        new_univ = set([])
        for e in b.universe():
            new_univ.add(t.eval(b,{Variable.x:e}))
        ok = ok and (new_univ == set([0,1,2,3]))
        new_univ = set([])
        for e in rs3.universe():
            new_univ.add(t.eval(rs3,{Variable.x:e}))
        ok = ok and (new_univ == set([0,1,2,3]))
        
        if ok:
            print make_readable(t)

    