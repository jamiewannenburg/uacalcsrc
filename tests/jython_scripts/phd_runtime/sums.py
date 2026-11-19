
from dmm import AbstractOperation, OperationSymbol, BasicAlgebra, add_arrow_residuation, semi_lattice_maximal, semi_lattice_minimal

# sum lattices
def sum_lattice(A,B):
    new_cardinality = A.cardinality() - 1 + B.cardinality()
    A_bot = semi_lattice_minimal(A)
    B_top = semi_lattice_maximal(B)
    Ap = [ i for i in range(A.cardinality()) if i != A_bot ]
    
    B_start = len(Ap) #A.cardinality() - 1
    
    joinA = A.getOperation(OperationSymbol("join",2))
    meetA = A.getOperation(OperationSymbol("meet",2))
    
    joinB = B.getOperation(OperationSymbol("join",2))
    meetB = B.getOperation(OperationSymbol("meet",2))
    
    class join_op(AbstractOperation):
        # place Ap above B
        def intValueAt(self,args):
            # both in Ap (note join is never bot)
            if args[0] < B_start and args[1] < B_start:
                return Ap.index(joinA.intValueAt([Ap[args[0]],Ap[args[1]]]))
            # both in B
            elif args[0] >= B_start and args[1] >= B_start:
                return B_start + joinB.intValueAt([args[0]-B_start,args[1]-B_start])
            # 0 in Ap and 1 in B
            elif args[0] < B_start and args[1] >= B_start:
                return args[0]
            # 0 in B and 1 in Ap
            else:
                return args[1]
                
    new_join = join_op('join', 2, new_cardinality)
    
    class meet_op(AbstractOperation):
        # place Ap above B
        def intValueAt(self,args):
            # both in Ap
            if args[0] < B_start and args[1] < B_start:
                meet_in_A = meetA.intValueAt([Ap[args[0]],Ap[args[1]]])
                if meet_in_A == A_bot:
                    return B_top + B_start
                else:
                    return Ap.index(meet_in_A)
            # both in B
            elif args[0] >= B_start and args[1] >= B_start:
                return B_start + meetB.intValueAt([args[0]-B_start,args[1]-B_start])
            # 0 in Ap and 1 in B
            elif args[0] < B_start and args[1] >= B_start:
                return args[1]
            # 0 in B and 1 in Ap
            else:
                return args[0]
                
    new_meet = meet_op('meet', 2, new_cardinality)
    
    ops = new_join,new_meet
    return BasicAlgebra(A.getName()+'+'+B.getName(), new_cardinality, ops)
    
def sum_brouwerian(A,B):
    S = sum_lattice(A,B)
    
    join = S.getOperation(OperationSymbol("join",2))
    meet = S.getOperation(OperationSymbol("meet",2))
    class e_op(AbstractOperation):
        def intValueAt(self,args):
            return semi_lattice_maximal(S)
    e = e_op("e", 0, S.cardinality())

    alg = BasicAlgebra(S.getName(), S.cardinality(), [join,meet,e])

    alg = add_arrow_residuation(alg,fusion_sym = 'meet')
    
    return alg
    
    
def sum_heyting(A,B):
    S = sum_brouwerian(A,B)
    
    join = S.getOperation(OperationSymbol("join",2))
    meet = S.getOperation(OperationSymbol("meet",2))
    e = S.getOperation(OperationSymbol("e",0))
    arrow = S.getOperation(OperationSymbol("arrow",2))

    class bot_op(AbstractOperation):
        def intValueAt(self,args):              
            return semi_lattice_minimal(S)
    bot = bot_op("bot", 0, S.cardinality())

    alg = BasicAlgebra(S.getName(), S.cardinality(), [join,meet,e,arrow,bot])

    return alg
    
# TODO improve by using and checking given constants?

if __name__=='__main__':
    # check if a certain sum satisfies Peirce's law
    import os
    import sys
    from dmm import AlgebraIO, equation_to_term, Variable, make_readable, check_brouwerian
    
    dir = 'input'
    # name = sys.argv[1]
    # alg_file_name = os.path.join(dir,"{}.ua".format(name))
    # if not os.path.isfile(alg_file_name):
        # raise Exception("Could not find: {}".format(alg_file_name))
    # alg = AlgebraIO.readAlgebraFile(alg_file_name)
    
    b2 = AlgebraIO.readAlgebraFile(os.path.join(dir,"Br2.ua"))
    A = AlgebraIO.readAlgebraFile(os.path.join(dir,"A_brouwerian.ua"))
    b4 = AlgebraIO.readAlgebraFile(os.path.join(dir,"Br2xBr2.ua"))
    
    alg = sum_brouwerian(b2,A)
    # alg = sum_brouwerian(b2,sum_brouwerian(b4,b4))
    # check_brouwerian(alg)
    # AlgebraIO.writeAlgebraFile(alg, os.path.join(dir,"Br2+A_brouwerian.ua"))
    
    peirce = equation_to_term(['join(arrow(y,x),arrow(arrow(arrow(x,y),x),x))','e()',[Variable.x,Variable.y]])
    result = peirce.findFailureMap(alg)
    if result:
        l = peirce.leftSide()
        r = peirce.rightSide()
        print "{} is does not satisfy Peirce's law as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
    