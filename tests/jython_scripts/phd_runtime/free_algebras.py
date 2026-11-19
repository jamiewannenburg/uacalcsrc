import sys
sys.path.append("uacalc.jar")

from org.uacalc.alg import FreeAlgebra, Subalgebra
from org.uacalc.terms import Variable
from org.uacalc.io import AlgebraIO
from org.uacalc.alg.op import OperationSymbol
from org.uacalc.util import IntArray
from dmm import to_term, make_readable
from isomorphism import check_isomorphism, is_isomorphic
import itertools

import os
in_dir = 'input'
out_dir = 'output'
name = sys.argv[1]


alg_file_name = os.path.join(in_dir,"{}.ua".format(name))
tex_file_name = os.path.join(out_dir,"{}_subalgebra.tex".format(name))
free_alg_file_name = os.path.join(in_dir,"{}_F1.ua".format(name))
sub_alg_file_name = os.path.join(in_dir,"{}_S.ua".format(name))

if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)
dot = alg.getOperation(OperationSymbol('dot',2))

free_alg = FreeAlgebra(alg, 1, True, True) 
AlgebraIO.writeAlgebraFile(free_alg, free_alg_file_name)
# free_alg = AlgebraIO.readAlgebraFile(free_alg_file_name)

prod_alg = free_alg.getProductAlgebra()
n = prod_alg.numberOfFactors

x = free_alg.getElementFromTerm(Variable.x)

e = free_alg.getElementFromTerm(to_term('e()'))
e_ind = free_alg.elementIndex(e)
f_ind = free_alg.getOperation(OperationSymbol('neg',1)).intValueAt([e_ind])
f = free_alg.getElement(f_ind)
one_ind = free_alg.getOperation(OperationSymbol('dot',2)).intValueAt([f_ind,f_ind])
one = free_alg.getElement(one_ind)
zero_ind = free_alg.getOperation(OperationSymbol('neg',1)).intValueAt([one_ind])
zero = free_alg.getElement(zero_ind)
# f = free_alg.getElementFromTerm(to_term('neg(e())'))
# one = free_alg.getElementFromTerm(to_term('dot(neg(e()),neg(e()))'))
# zero = free_alg.getElementFromTerm(to_term('neg(dot(neg(e()),neg(e())))'))

e_alg = e.get(0)
f_alg = f.get(0)
one_alg = one.get(0)
zero_alg = zero.get(0)

c4 = [ e_alg, f_alg, one_alg, zero_alg]

generators = []#e_ind,f_ind,one_ind,zero_ind
for i in range(alg.cardinality()):
    if not i in c4:
        if dot.intValueAt([i,i]) == one.get(0):
            el = f.clone()
            el.set(2,i)
        else:
            el = e.clone()
            el.set(2,i)
        generators.append(free_alg.elementIndex(el))

# sub_alg = Subalgebra(free_alg,generators)
sub_alg = free_alg.sub().Sg(generators)
    
if not is_isomorphic(alg,sub_alg):
    print "Guess is not a subalgebra of the 1-generated free algebra."
else:
    full_tex_path = os.path.join('uacalc',out_dir,name)
    full_tex_path = full_tex_path.replace('\\','/')
    tex = ""
    # tex += "\\input{%s}\n\n"%(full_tex_path)
    tex += "$$ \\#F_1({})={} $$ \n\n".format(alg.getName(),free_alg.cardinality())
    tex += "$$ x={} $$ \n\n".format(x)
    
    tex += r"\begin{tabular}{|cc|}"+'\n'
    tex += r"\hline"+'\n'
    for i in range(sub_alg.cardinality()):
        element = sub_alg.getElement(i)
        tex += "${}$ & ${}$ \\\\\n".format( make_readable(free_alg.getTerm(element),translation='latex'), element )
    tex += r"\hline"+'\n'
    tex += r"\end{tabular}"+'\n\n\n'
        
    with open(tex_file_name,'w') as f:
        f.write(tex)
    