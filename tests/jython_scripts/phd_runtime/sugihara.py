from dmm import BasicAlgebra,AlgebraIO,AbstractOperation,add_arrow_and_meet,check_dmm
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')

def ua2int(a,n):
    odd = n%2
    if not odd:
        if a-n/2 < 0:
            return a-n/2
        else:
            return a-n/2+1
    else:
        return a-((n-1)/2)

def int2ua(a,n):
    odd = n%2
    if not odd:
        if a==0:
            raise Exception("Odd SMs don't have 0")
        if a>0:
            return a+n/2-1
        else:
            return a+n/2
    else:
        return a+((n-1)/2)

def get_sugihara_monoid(n):
    if n < 1:
        raise Exception("Can not have empty universe.")
    odd = n%2
    
    class e_op(AbstractOperation):
        def intValueAt(self,args):
            if odd:
                return int2ua(0,n)
            else:
                return int2ua(1,n)
    e = e_op('e', 0, n)
    
    class neg_op(AbstractOperation):
        def intValueAt(self,args):
            return int2ua(-ua2int(args[0],n),n)
    neg = neg_op('neg', 1, n)
    
    class join_op(AbstractOperation):
        def intValueAt(self,args):
            sm1 = ua2int(args[0],n)
            sm2 = ua2int(args[1],n)
            if sm1 <= sm2:
                return args[1]
            else:
                return args[0]
    join = join_op('join', 2, n)
    
    class dot_op(AbstractOperation):
        def intValueAt(self,args):
            sm1 = ua2int(args[0],n)
            sm2 = ua2int(args[1],n)
            if abs(sm1) == abs(sm2):
                return int2ua(min(sm1,sm2),n)
            elif abs(sm1) < abs(sm2):
                return args[1]
            else:
                return args[0]
    dot = dot_op('dot', 2, n)
    
    ops = [e,neg,join,dot]
    alg = BasicAlgebra("S_%s"%(n), n, ops)
    return add_arrow_and_meet(alg)
    
def get_sugihara_algebra(n):
    if n < 1:
        raise Exception("Can not have empty universe.")
    odd = n%2
        
    class neg_op(AbstractOperation):
        def intValueAt(self,args):
            return int2ua(-ua2int(args[0],n),n)
    neg = neg_op('neg', 1, n)
    
    class join_op(AbstractOperation):
        def intValueAt(self,args):
            sm1 = ua2int(args[0],n)
            sm2 = ua2int(args[1],n)
            if sm1 <= sm2:
                return args[1]
            else:
                return args[0]
    join = join_op('join', 2, n)
    
    class meet_op(AbstractOperation):
        def intValueAt(self,args):
            sm1 = ua2int(args[0],n)
            sm2 = ua2int(args[1],n)
            if sm1 >= sm2:
                return args[1]
            else:
                return args[0]
    meet = meet_op('meet', 2, n)
    
    class arrow_op(AbstractOperation):
        def intValueAt(self,args):
            sm1 = ua2int(args[0],n)
            sm2 = ua2int(args[1],n)
            if sm1 <= sm2:
                return int2ua(max(-sm1,sm2),n)
            else:
                return int2ua(min(-sm1,sm2),n)
    arrow = arrow_op('arrow', 2, n)
    
    ops = [neg,join,meet,arrow]
    alg = BasicAlgebra("S_%s"%(n), n, ops)
    return alg
    
if __name__ == '__main__':
    # # check that S_4 and S_5 are DMMs
    # s4 = get_sugihara_monoid(4)
    # check_dmm(s4,example=True)
    
    # s5 = get_sugihara_monoid(5)
    # check_dmm(s5,example=True)
    import sys
    # get arguments n and optional monoid/algebra
    n = int(sys.argv[1])
    if len(sys.argv) > 2:
        if sys.argv[2] == 'monoid':
            alg = get_sugihara_monoid(n)
            filename = os.path.join(dir,"s%s.ua"%(n))
        elif sys.argv[2] == 'algebra':
            alg = get_sugihara_algebra(n)
            filename = os.path.join(dir,"sa%s.ua"%(n))
        else:
            raise Exception("Invalid argument. Must be monoid or algebra.")
    else:
        alg = get_sugihara_monoid(n)
        filename = os.path.join(dir,"s%s.ua"%(n))
    AlgebraIO.writeAlgebraFile(alg, filename)