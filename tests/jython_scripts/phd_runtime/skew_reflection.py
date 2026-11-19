# import itertools
import os
import sys

from dmm import check_type, add_arrow_and_meet, BasicAlgebra, AlgebraIO, AbstractOperation, OperationSymbol, TermOperationImp, VariableImp, Variable

def slaney(alg):
    dot = alg.getOperation(OperationSymbol("dot",2))
    meet = alg.getOperation(OperationSymbol("meet",2))
    join = alg.getOperation(OperationSymbol("join",2))
    arrow = alg.getOperation(OperationSymbol("arrow",2))
    e = alg.getOperation(OperationSymbol("e",0))
    monus = alg.getOperation(OperationSymbol("monus",2))
    
    # contruct new algebra
    new_cardinality = alg.cardinality()*2 + 2

    class neg_op(AbstractOperation):
        def intValueAt(self,args):
            return -args[0]+new_cardinality-1
            
    new_neg = neg_op('neg', 1, new_cardinality)
    # for i in range(new_cardinality):
        # print i,new_neg.intValueAt([i])

    class e_op(AbstractOperation):
        def intValueAt(self,args):
            return e.intValueAt(args)+1
            
    new_e = e_op('e', 0, new_cardinality)

    class dot_op(AbstractOperation):
        def intValueAt(self,args):
            if args[0] == 0 or args[1] == 0:
                return 0
            elif args[0] == new_cardinality-1 or args[1] == new_cardinality-1:
                return new_cardinality-1
            elif args[0] <= alg.cardinality() and args[1] <= alg.cardinality():
                return dot.intValueAt([args[0]-1,args[1]-1]) + 1
            elif args[0] <= alg.cardinality():
                return new_neg.intValueAt([arrow.intValueAt([args[0]-1,new_neg.intValueAt([args[1]])-1]) + 1])
            elif args[1] <= alg.cardinality():
                return new_neg.intValueAt([arrow.intValueAt([args[1]-1,new_neg.intValueAt([args[0]])-1]) + 1])
            else:
                return new_cardinality-1
            
    new_dot = dot_op('dot', 2, new_cardinality)

    class join_op(AbstractOperation):
        def intValueAt(self,args):
            if args[0] == new_cardinality-1 or args[1] == new_cardinality-1:
                return new_cardinality-1
            elif args[0] == 0:
                return args[1]
            elif args[1] == 0:
                return args[0]
            elif args[0] <= alg.cardinality() and args[1] <= alg.cardinality():
                return join.intValueAt([args[0]-1,args[1]-1]) + 1
            elif args[0] <= alg.cardinality():
                return new_neg.intValueAt([monus.intValueAt([new_neg.intValueAt([args[1]])-1,args[0]-1]) + 1])
            elif args[1] <= alg.cardinality():
                return new_neg.intValueAt([monus.intValueAt([new_neg.intValueAt([args[0]])-1,args[1]-1]) + 1])
            else:
                return new_neg.intValueAt([meet.intValueAt([new_neg.intValueAt([args[1]])-1,new_neg.intValueAt([args[0]])-1]) + 1])
            
    new_join = join_op('join', 2, new_cardinality)

    ops = new_join,new_neg,new_e,new_dot
    return BasicAlgebra(alg.getName(), new_cardinality, ops)

def reflection_monus(alg):
    class monus_op(AbstractOperation):
        def intValueAt(self,args):
            return args[0]
    return monus_op('monus', 2, alg.cardinality())

def weaved_monus(alg):
    meet = alg.getOperation(OperationSymbol("meet",2))
    neg = alg.getOperation(OperationSymbol("neg",1))
    class monus_op(AbstractOperation):
        def intValueAt(self,args):
            return meet.intValueAt([args[0],neg.intValueAt(args[1])])
            
    return monus_op('monus', 2, alg.cardinality())

# make dunn monoid reduct (all non-zero points whose square is not top)
# it is the inverse of the above (with a monus)
def dunn_reduct(alg):
    new_cardinality = alg.cardinality()/2 - 1
    dot = alg.getOperation(OperationSymbol("dot",2))
    arrow = alg.getOperation(OperationSymbol("arrow",2))
    join = alg.getOperation(OperationSymbol("join",2))
    meet = alg.getOperation(OperationSymbol("meet",2))
    neg = alg.getOperation(OperationSymbol("neg",1))
    e = alg.getOperation(OperationSymbol("e",0))
    
    class dot_op(AbstractOperation):
        def intValueAt(self,args):
            return dot.intValueAt([args[0]+1,args[1]+1])-1
    new_dot = dot_op('dot', 2, new_cardinality)
    
    class arrow_op(AbstractOperation):
        def intValueAt(self,args):
            return arrow.intValueAt([args[0]+1,args[1]+1])-1
    new_arrow = arrow_op('arrow', 2, new_cardinality)
    
    class join_op(AbstractOperation):
        def intValueAt(self,args):
            return join.intValueAt([args[0]+1,args[1]+1])-1
    new_join = join_op('join', 2, new_cardinality)
    
    class meet_op(AbstractOperation):
        def intValueAt(self,args):
            return meet.intValueAt([args[0]+1,args[1]+1])-1
    new_meet = meet_op('meet', 2, new_cardinality)
    
    class monus_op(AbstractOperation):
        def intValueAt(self,args):
            return meet.intValueAt([args[0]+1,neg.intValueAt(args[1]+1)])-1
    new_monus = monus_op('monus', 2, new_cardinality)
    
    class e_op(AbstractOperation):
        def intValueAt(self,args):
            return e.intValueAt(args)-1
    new_e = e_op('e', 0, new_cardinality)
    
    ops = new_join,new_meet,new_dot,new_arrow,new_monus,new_e
    return BasicAlgebra(alg.getName()+'^-', new_cardinality, ops)
    

if __name__=='__main__':
    dir = 'input'
    name = sys.argv[1]
    alg_file_name = os.path.join(dir,"{}.ua".format(name))
    if not os.path.isfile(alg_file_name):
        raise Exception("Could not find: {}".format(alg_file_name))
        
    alg = AlgebraIO.readAlgebraFile(alg_file_name)
    
    if len(sys.argv)<3:
        monus = alg.getOperation(OperationSymbol("monus",2))
        if monus == None:
            raise Exception("Algebra must have monus operation or specify the type in second argument, e.g. reflection or weaved.")
        else:
            wan_alg = alg
            wan_alg.setName("S(%s)"%(alg.getName()))
            type = 'skew'
            
    elif sys.argv[2]=='reflection':
        monus = reflection_monus(alg)
        ops = alg.operations()
        new_ops = []
        for op in ops:
            new_ops.append(op)
        new_ops.append(monus)
        wan_alg =  BasicAlgebra("R(%s)"%(alg.getName()), alg.cardinality(), new_ops)
        type = 'reflection'
    elif sys.argv[2]=='weaved':
        neg = alg.getOperation(OperationSymbol("neg",1))
        if neg == None:
            raise Exception("Algebra must have negation to build the weaved construction.")
        monus = weaved_monus(alg)
        
        ops = alg.operations()
        new_ops = []
        for op in ops:
            new_ops.append(op)
        new_ops.append(monus)
        wan_alg = BasicAlgebra("W(%s)"%(alg.getName()), alg.cardinality(), new_ops)
        type = 'weaved'
    else:
        raise Exception("Reflection options are reflection or weaved.")
        
    new_alg = slaney(wan_alg)
    new_alg = add_arrow_and_meet(new_alg)
    alg_out_file_name = os.path.join(dir,"{}_{}.ua".format(name,type))
    AlgebraIO.writeAlgebraFile(new_alg, alg_out_file_name)
