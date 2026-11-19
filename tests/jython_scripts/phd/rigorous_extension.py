# CPython harness: copied from Jamie's PhD tree (read-only); path roots are relative to this file.
# Changes: none to logic; inputs live under tests/jython_scripts/phd/input/.
import sys
import os
import re

dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')

sys.path.append("uacalc.jar")

# from java.lang import System 
# from java.io import PrintStream, OutputStream
# class NoOutputStream(OutputStream):         
    # def write(self, b, off, len): pass      
    
# oldOut = System.out
# System.setOut(PrintStream(NoOutputStream()))
# sys.stdout = oldOut

from org.uacalc.alg import BasicAlgebra
from org.uacalc.io import AlgebraIO
from org.uacalc.alg.op import AbstractOperation,OperationSymbol

def get_rigorous_extension(alg):
    
    dot = alg.getOperation(OperationSymbol("dot",2))
    meet = alg.getOperation(OperationSymbol("meet",2))
    join = alg.getOperation(OperationSymbol("join",2))
    arrow = alg.getOperation(OperationSymbol("arrow",2))
    e = alg.getOperation(OperationSymbol("e",0))
    neg = alg.getOperation(OperationSymbol("neg",1))
    
    # contruct new algebra
    new_cardinality = alg.cardinality()+ 2
    ops = []
    # 0 will be new bottom and new_cardinality-1 will be new top

    # add lattice operations
    if meet:
        class meet_op(AbstractOperation):
            def intValueAt(self,args):
                if args[0] == 0 or args[1] == 0:
                    return 0
                elif args[0] == new_cardinality-1:
                    return args[1]
                elif args[1] == new_cardinality-1:
                    return args[0]
                else:
                    return meet.intValueAt([args[0]-1,args[1]-1]) + 1
                    
        meet_op = meet_op("meet", 2, new_cardinality)
        ops.append(meet_op)
    
    if join:
        class join_op(AbstractOperation):
            def intValueAt(self,args):
                if args[0] == new_cardinality-1 or args[1] == new_cardinality-1:
                    return new_cardinality-1
                elif args[0] == 0:
                    return args[1]
                elif args[1] == 0:
                    return args[0]
                else:
                    return join.intValueAt([args[0]-1,args[1]-1]) + 1
                    
        join_op = join_op("join", 2, new_cardinality)
        ops.append(join_op)

    # add residual operations
    if dot:
        class dot_op(AbstractOperation):
            def intValueAt(self,args):
                if args[0] == 0 or args[1] == 0:
                    return 0
                elif args[0] == new_cardinality-1 or args[1] == new_cardinality-1:
                    return new_cardinality-1
                else:
                    return dot.intValueAt([args[0]-1,args[1]-1]) + 1

        dot_op = dot_op("dot", 2, new_cardinality)
        ops.append(dot_op)
    
    if arrow:
        class arrow_op(AbstractOperation):
            def intValueAt(self,args):
                if args[0] == 0:
                    return new_cardinality-1
                elif args[1] == new_cardinality-1:
                    return new_cardinality-1
                elif args[0] == new_cardinality-1:
                    return 0
                elif args[1] == 0:
                    return 0
                else:
                    return arrow.intValueAt([args[0]-1,args[1]-1]) + 1
                    
        arrow_op = arrow_op("arrow", 2, new_cardinality)
        ops.append(arrow_op)
    
    if e:
        class e_op(AbstractOperation):
            def intValueAt(self,args):
                return e.intValueAt(args) + 1

        e_op = e_op("e", 0, new_cardinality)
        ops.append(e_op)

    if neg:
        class neg_op(AbstractOperation):
            def intValueAt(self,args):
                if args[0] == new_cardinality-1:
                    return 0
                elif args[0] == 0:
                    return new_cardinality-1
                else:
                    return neg.intValueAt([args[0]-1]) + 1

        neg_op = neg_op("neg", 1, new_cardinality)
        ops.append(neg_op)

    alg = BasicAlgebra("re("+alg.getName()+")", new_cardinality, ops)
    return alg

if __name__ == "__main__":
    import sys
    alg_name = sys.argv[1]
    alg_file_name = os.path.join(dir,"{}.ua".format(alg_name))
    if not os.path.isfile(alg_file_name):
        raise Exception("Could not find: {}".format(alg_file_name))
    alg = AlgebraIO.readAlgebraFile(alg_file_name)
    new_alg = get_rigorous_extension(alg)
    new_alg_file_name = os.path.join(dir,"{}_re.ua".format(alg_name))
    AlgebraIO.writeAlgebraFile(new_alg, new_alg_file_name)