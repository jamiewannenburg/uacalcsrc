import os
import sys
from dmm import AlgebraIO, AbstractOperation, BasicAlgebra, add_dual_lattice_operation, add_arrow_residuation, check_heyting, semi_lattice_minimal,semi_lattice_maximal

dir = 'input'
name = sys.argv[1]
alg_file_name = os.path.join(dir,"{}.ua".format(name))
if not os.path.isfile(alg_file_name):
    raise Exception("Could not find: {}".format(alg_file_name))

alg = AlgebraIO.readAlgebraFile(alg_file_name)

alg = add_dual_lattice_operation(alg)
alg = add_arrow_residuation(alg,fusion_sym = 'meet')

# add e and bot

op_syms = alg.similarityType().getOperationSymbols()
ops = []
for op in op_syms:
    ops.append(alg.getOperation(op))
op_syms = [str(o) for o in op_syms]

if not 'e' in op_syms:
    class e_op(AbstractOperation):
        def intValueAt(self,args):                    
            return semi_lattice_maximal(alg)
    
    op = e_op("e", 0, alg.cardinality())
    ops.append(op)
    
if not 'bot' in op_syms:
    class bot_op(AbstractOperation):
        def intValueAt(self,args):                    
            return semi_lattice_minimal(alg)
    
    op = bot_op("bot", 0, alg.cardinality())
    ops.append(op)
    
alg = BasicAlgebra(alg.getName(), alg.cardinality(), ops)

# write in complete signature
AlgebraIO.writeAlgebraFile(alg, alg_file_name)

if check_heyting(alg):
    print "{} is a Heyting algebra".format(alg.getName())