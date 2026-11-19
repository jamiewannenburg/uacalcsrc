from dmm import BasicAlgebra,AlgebraIO,OperationSymbol,Terms,TermOperationImp,Variable,make_readable,equation_to_term

def add_iff(alg):
    join = alg.getOperation(OperationSymbol("join",2))
    meet = alg.getOperation(OperationSymbol("meet",2))
    neg = alg.getOperation(OperationSymbol("neg",1))
    e = alg.getOperation(OperationSymbol("e",0))
    dot = alg.getOperation(OperationSymbol("dot",2))
    arrow = alg.getOperation(OperationSymbol("arrow",2))

    # add iff
    iff_term = Terms.stringToTerm('meet(arrow(x,y),arrow(y,x))')
    iff = TermOperationImp('iff', iff_term, iff_term.getVariableList(), alg)

    ops = join,meet,neg,e,dot,arrow,iff
    return BasicAlgebra(alg.getName(), alg.cardinality(), ops)

# check associativity
def check_iff_associativity(alg):
    iff_alg = add_iff(alg)
    eq = equation_to_term(['iff(iff(x,y),z)','iff(x,iff(y,z))',[Variable.x,Variable.y,Variable.z]])
    result = eq.findFailureMap(iff_alg)
    if result:
            l = eq.leftSide()
            r = eq.rightSide()
            print "{} is not associative as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
            return False
    else:
        print "iff is associative in {}".format(alg.getName())
        return True
            
if __name__ == '__main__':
    from sugihara import get_sugihara_monoid
    s8 = get_sugihara_monoid(8)
    check_iff_associativity(s8)
    AlgebraIO.writeAlgebraFile(add_iff(s8), "input/s8.ua")
    
    b2 = AlgebraIO.readAlgebraFile("input/b2.ua")
    check_iff_associativity(b2)
    
    s3 = AlgebraIO.readAlgebraFile("input/s3.ua")
    check_iff_associativity(s3)
    