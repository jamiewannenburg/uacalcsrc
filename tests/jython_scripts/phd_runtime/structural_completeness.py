import sys
sys.path.append("uacalc.jar")

from org.uacalc.io import AlgebraIO
from org.uacalc.terms import NonVariableTerm,Variable
from org.uacalc.eq import Equation
from dmm import to_term, make_readable
import itertools

import os
in_dir = 'input'
out_dir = 'output'
name = 'c4_weaved'
# name = 's3_weaved'

alg_file_name = os.path.join(in_dir,"{}.ua".format(name))
# tex_file_name = os.path.join(out_dir,"{}_subalgebra.tex".format(name))

if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)

terms_str = ['0','arrow(x,e())','e()','x','dot(x,x)','arrow(x,neg(x))','neg(x)','f','dot(x,f)','1']
# terms_str = ['0','arrow(x,e())','e()','x','neg(x)','f','dot(x,f)','1']
terms = [to_term(i) for i in terms_str]

# x_str = 'join(e(),meet(x,f))'
# x_str = 'arrow(join(meet(x,e()),meet(e(),arrow(neg(x),arrow(x,x)))),e())'
# x_str = 'join(e(),meet(x,dot(neg(x),neg(x))))'
x_str = 'join(e(),meet(meet(x,f),dot(neg(x),neg(x))))'
x = to_term(x_str)
if x.intEval(alg,{Variable.x: 3}) != 3:
    raise Exception("This term does not map x back to x in the original algebra.")

new_terms = [ t.substitute({Variable.x: x}) for t in terms]

for op in alg.operations():
    print "Checking {}".format(op.symbol())
    for tup in itertools.product(range(alg.cardinality()),repeat=op.arity()):
        val = op.intValueAt(tup)
        t2 = NonVariableTerm(op.symbol(),[new_terms[i] for i in tup])
        # print t2
        eq = Equation(new_terms[val],t2)
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            print "In {0} {3}={1}({2}) but does not satisfy {4}={5} at {6}.".format(alg.getName(),op.symbol(),','.join([str(i) for i in tup]),val,make_readable(l),make_readable(r),result)#  
            break