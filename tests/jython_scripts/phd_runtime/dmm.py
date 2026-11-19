import sys
sys.path.append("uacalc.jar")
sys.path.append("LatDraw.jar")
import pyparsing as pp
import re
import os

from java.lang import System 
from java.io import PrintStream, OutputStream
class NoOutputStream(OutputStream):         
    def write(self, b, off, len): pass      
    
oldOut = System.out
System.setOut(PrintStream(NoOutputStream()))
sys.stdout = oldOut

from org.uacalc.alg import BasicAlgebra
from org.uacalc.io import AlgebraIO
from org.uacalc.alg.op import AbstractOperation,OperationSymbol,TermOperationImp
from org.uacalc.terms import Terms, Variable, NonVariableTerm, VariableImp
from org.uacalc.eq import Equation

from org.uacalc.lat import Lattices

convert_dict = {
    'unicode': {
        'join':u'\u2228',
        'neg':u'\u00AC',
        'dot':u'\u00B7',
        'e':u'e',
        'meet':u'\u2227',
        'arrow':u'\u2192',
        'iff':u'\u2194',
        },
    'html': {
        'join':'&or;',
        'neg':'&not;',
        'dot':'&middot;',
        'e':'e',
        'meet':'&and;',
        'arrow':'&rarr;',
        'iff':'&harr;',
    },
    'latex': {
        'join':'\\vee ',
        'neg':'\\neg ',
        'dot':'\\cdot ',
        'e':'e ',
        'meet':'\\wedge ',
        'arrow':'\\to ',
        'iff':'\\leftrightarrow ',
    },
    'ascii': {
        'join':'v',
        'neg':'-',
        'dot':'.',
        'e':'e',
        'meet':'^',
        'arrow':'->',
        'iff':'<->',
        'zero':'0',
        'one':'1',
        'comp':'-'
    }
}

def translate(op,translation='ascii'):
    try:
        return convert_dict[translation][op]
    except KeyError:
        return op

# parse terms of De Morgan monoids

e = 'e'+pp.Suppress('()')
bot = 'bot'+pp.Suppress('()')
top = 'top'+pp.Suppress('()')
f = 'f'+pp.Suppress('()')
x = pp.Word('xyz0123456789_')

# full dmm
def make_expr_full():
    expr = pp.Forward()
    
    dot =   'dot'     +pp.Suppress('(')+ expr +pp.Suppress(',')+ expr +pp.Suppress(')')
    join =  'join'    +pp.Suppress('(')+ expr +pp.Suppress(',')+ expr +pp.Suppress(')')
    meet =  'meet'    +pp.Suppress('(')+ expr +pp.Suppress(',')+ expr +pp.Suppress(')')
    arrow = 'arrow'   +pp.Suppress('(')+ expr +pp.Suppress(',')+ expr +pp.Suppress(')')
    iff = 'iff'       +pp.Suppress('(')+ expr +pp.Suppress(',')+ expr +pp.Suppress(')')
    neg =   'neg'     +pp.Suppress('(')+ expr +pp.Suppress(')')

    expr  << (e | bot | top | f | dot | join | meet | arrow | iff | neg | x)
    return expr

def _to_term(s,l,t):
    op = t[0]
    args = t[1:]
    if op == 'iff':
        xtoy = NonVariableTerm(OperationSymbol('arrow',2),[args[0],args[1]])
        ytox = NonVariableTerm(OperationSymbol('arrow',2),[args[1],args[0]])
        return NonVariableTerm(OperationSymbol('meet',2),[xtoy,ytox])
    elif len(args) > 0:
        return NonVariableTerm(OperationSymbol(op,len(args)),args)
    elif op in ['e','f','top','bot']:
        return NonVariableTerm.makeConstantTerm(OperationSymbol(op,0))
    else:
        return VariableImp(op)
        
    
expr_full = make_expr_full()
expr_full.setParseAction(_to_term)

find_0 = re.compile(r'(?<=[\(,])0(?=[,\)])|^0$')
find_1 = re.compile(r'(?<=[\(,])1(?=[,\)])|^1$')
find_f = re.compile(r'(?<=[\(,])f(?=[,\)])|^f$')
find_e = re.compile(r'(?<=[\(,])e(?=[,\)])|^e$')

def to_term(mystr):
    mystr = find_0.sub(r'neg(1)',mystr)
    mystr = find_1.sub(r'dot(f,f)',mystr)
    mystr = find_f.sub(r'neg(e)',mystr)
    mystr = find_e.sub(r'e()',mystr)
    return expr_full.parseString(mystr)[0]
    
    
def make_readable(term,translation='ascii'):
    if term.isaVariable():
        return term.toString()
    
    opsym = term.leadingOperationSymbol()
    op = opsym.name()
    arity = opsym.arity()
    
    if arity == 0:
        return translate(op,translation)
    elif arity == 1:
        return translate(op,translation)+make_readable(term.getChildren()[0],translation)
    elif arity == 2:
        args = term.getChildren()
        return "("+make_readable(args[0],translation) + translate(op,translation) + make_readable(args[1],translation)+")"
    else:
        return translate(op,translation)+'('+','.join([ make_readable(t,translation) for t in term.getChildren()])+')'

def equation_to_term(x): 
    l_term = to_term(x[0])
    r_term = to_term(x[1])
    return Equation(l_term,r_term,x[2])
    
def leq(eqs):
    return ['join(%s,%s)'%(eqs[0],eqs[1])]+eqs[1:]
    
lattice_axioms = [
    ['join(x,x)','x',[Variable.x]],
    ['join(x,y)','join(y,x)',[Variable.x,Variable.y]],
    ['join(x,join(y,z))','join(join(x,y),z)',[Variable.x,Variable.y,Variable.z]],
    ['meet(x,x)','x',[Variable.x]],
    ['meet(x,y)','meet(y,x)',[Variable.x,Variable.y]],
    ['meet(x,meet(y,z))','meet(meet(x,y),z)',[Variable.x,Variable.y,Variable.z]],
    ['meet(x,join(x,y))','x',[Variable.x,Variable.y]],
    ['join(x,meet(x,y))','x',[Variable.x,Variable.y]],
]
lattice_axioms = map(equation_to_term,lattice_axioms)

crl_axioms = [
    # commutative monoid operations
    ['dot(x,y)','dot(y,x)',[Variable.x,Variable.y]],
    ['dot(x,e())','x',[Variable.x]],
    ['dot(x,dot(y,z))','dot(dot(x,y),z)',[Variable.x,Variable.y,Variable.z]],
    # crl axioms
    leq(['x','arrow(y,dot(y,x))',[Variable.x,Variable.y]]),
    leq(['dot(x,arrow(x,y))','y',[Variable.x,Variable.y]]),
    leq(['dot(x,meet(y,z))','meet(dot(x,y),dot(x,z))',[Variable.x,Variable.y,Variable.z]]),
    ['meet(arrow(x,y),arrow(x,z))','arrow(x,meet(y,z))',[Variable.x,Variable.y,Variable.z]],
]
crl_axioms = lattice_axioms + map(equation_to_term,crl_axioms)
# crl_axioms = map(equation_to_term,crl_axioms)

icrl_axioms = [
    # involution
    ['x','neg(neg(x))',[Variable.x]],
    # leq(['dot(x,neg(join(dot(x,y),z)))','neg(y)']),
    # leq(['neg(join(x,y))','neg(x)']),
    ['neg(x)','arrow(x,neg(e()))',[Variable.x]],
]
icrl_axioms = crl_axioms + map(equation_to_term,icrl_axioms)

lattice_distributivity = equation_to_term(['meet(x,join(y,z))','join(meet(x,y),meet(x,z))',[Variable.x,Variable.y,Variable.z]])
square_increasing = equation_to_term( leq(['x','dot(x,x)',[Variable.x]]) )

brouwerian_axioms = [
    # commutative monoid operations
    leq(['x','e()',[Variable.x]]),
]
brouwerian_axioms = crl_axioms + [square_increasing] + map(equation_to_term,brouwerian_axioms)

dmm_axioms = icrl_axioms + [lattice_distributivity, square_increasing]
# dmm_axioms = icrl_axioms + [square_increasing]
dunn_axioms = crl_axioms + [lattice_distributivity, square_increasing]

m_axioms = [
    leq(['e','f',[]]),
    leq(['x','1',[Variable.x]]),
    ['arrow(join(arrow(x,e()),arrow(neg(x),e())),0)','neg(dot(f,f))',[Variable.x]]
]
m_axioms = dmm_axioms + map(equation_to_term,m_axioms)

c4_axioms = [
    leq(['e()','f',[]]),
    leq(['x','1',[Variable.x]]),
    leq(['arrow(x,e())','join(x,arrow(x,0))',[Variable.x]]),
    leq(['meet(x,arrow(x,f))','join(arrow(x,e()),arrow(f,x))',[Variable.x]]),
    leq(['e()','join(arrow(x,y),arrow(y,x))',[Variable.x,Variable.y]]),
]

c4_axioms = dmm_axioms + map(equation_to_term,c4_axioms)

simple_chain_axioms = [
    ['dot(x,dot(y,z))','dot(dot(x,y),z)',[Variable.x,Variable.y,Variable.z]],
    leq(['x','arrow(y,dot(y,x))',[Variable.x,Variable.y]]),
    leq(['dot(x,arrow(x,y))','y',[Variable.x,Variable.y]]),
    leq(['dot(x,meet(y,z))','meet(dot(x,y),dot(x,z))',[Variable.x,Variable.y,Variable.z]]),
    ['meet(arrow(x,y),arrow(x,z))','arrow(x,meet(y,z))',[Variable.x,Variable.y,Variable.z]],
    ['neg(x)','arrow(x,neg(e()))',[Variable.x]],
]
simple_chain_axioms = map(equation_to_term,simple_chain_axioms)

# helpfull functions
def check_type(alg):
    dot = alg.getOperation(OperationSymbol("dot",2))
    arrow = alg.getOperation(OperationSymbol("arrow",2))
    join = alg.getOperation(OperationSymbol("join",2))
    meet = alg.getOperation(OperationSymbol("meet",2))
    neg = alg.getOperation(OperationSymbol("neg",1))
    e = alg.getOperation(OperationSymbol("e",0))
    f = alg.getOperation(OperationSymbol("f",0))
    if meet == None and join == None:
        return False
    if neg == None and f == None:
        return False
    if dot == None and arrow == None:
        return False
    if neg == None and arrow == None:
        return False
    return True
    
def check_full(alg):
    dot = alg.getOperation(OperationSymbol("dot",2))
    arrow = alg.getOperation(OperationSymbol("arrow",2))
    join = alg.getOperation(OperationSymbol("join",2))
    meet = alg.getOperation(OperationSymbol("meet",2))
    e = alg.getOperation(OperationSymbol("e",0))
    neg = alg.getOperation(OperationSymbol("neg",1))
    return not None in [dot,meet,arrow,join,e,neg]
    
def add_arrow_and_meet(alg):
    alg = add_dual_lattice_operation(alg)
    alg = add_arrow_residuation(alg)
    return alg

def add_missing_ops(alg):
    op_syms = alg.similarityType().getOperationSymbols()
    op_syms = [str(o) for o in op_syms]
    if not 'neg' in op_syms:
        alg = add_neg(alg)
    if not 'meet' in op_syms or not 'join' in op_syms:
        alg = add_dual_lattice_operation(alg)
    if not 'dot' in op_syms or not 'arrow' in op_syms:
        alg = add_dual_residuation_operation(alg)
    return alg
    
def get_dual_lattice_operation(alg):
    op_syms = alg.similarityType().getOperationSymbols()
    op_syms = [str(o) for o in op_syms]
    
    # none are there, so can't construct one from the other
    if not ('join' in op_syms or 'meet' in op_syms):
        raise Exception("Either join or meet needs to be defined.")
    
    # get the names of the available operation and its dual
    lops = ['meet','join']
    j = 'join' in op_syms
    op_sym = lops[j]
    dual_sym = lops[not j]
    
    # assume neg is a demorgan involution to construct dual operation
    if 'neg' in op_syms:
        term = Terms.stringToTerm('neg({}(neg(x),neg(y)))'.format(op_sym))
        op = TermOperationImp(dual_sym,term,[Variable.x,Variable.y],alg)
    else:
        given = alg.getOperation(OperationSymbol(op_sym,2))
        class dual_op(AbstractOperation):
            def intValueAt(self,args):
                x,y = args
                
                bounds = []
                for z in alg.universe():
                    if given.intValueAt([x,z]) == x and given.intValueAt([y,z]) == y:
                        bounds.append(z)
                if len(bounds) == 0:
                    raise Error('{} and {} have no {} bound'.format(x,y,'lower' if j else 'upper'))
                elif len(bounds) == 1:
                    z = bounds[0]
                else:
                    z = bounds[0]
                    for zp in bounds[1:]:
                        z = given.intValueAt([z,zp])
                        
                return z
        op = dual_op(dual_sym, 2, alg.cardinality())
    
    return op
    
def add_dual_lattice_operation(alg):
    op_syms = alg.similarityType().getOperationSymbols()
    ops = []
    for op in op_syms:
        ops.append(alg.getOperation(op))
    op_syms = [str(o) for o in op_syms]
    
    # both already there
    if 'join' in op_syms and 'meet' in op_syms:
        return alg
    
    op = get_dual_lattice_operation(alg)
    ops.append(op)
    new_alg = BasicAlgebra(alg.getName(), alg.cardinality(), ops)
    return new_alg
    
def add_neg(alg):
    op_syms = alg.similarityType().getOperationSymbols()
    ops = []
    for op in op_syms:
        ops.append(alg.getOperation(op))
    op_syms = [str(o) for o in op_syms]
    
    # both already there
    if 'neg' in op_syms:
        return alg
    
    
    # assume neg is constructed form resitual and constant
    bo = None
    if 'arrow' in op_syms:
        arrow = alg.getOperation(OperationSymbol('arrow',2))
        if 'f' in op_syms:
            bot = alg.getOperation(OperationSymbol('f',0))
            bo = bot.intValueAt([])
        elif 'bot' in op_syms:
            bot = alg.getOperation(OperationSymbol('bot',0))
            bo = bot.intValueAt([])
    # if these operations don't exist just ignore
    if bo == None:
        return alg
    # else
    print(bo)
    class neg_op(AbstractOperation):
        def intValueAt(self,args):
            x = args[0]
            return arrow.intValueAt([x,bo])
    op = neg_op('neg', 1, alg.cardinality())
    ops.append(op)
    new_alg = BasicAlgebra(alg.getName(), alg.cardinality(), ops)
    return new_alg
    
    
    
def semi_lattice_leq(alg):
    op_syms = alg.similarityType().getOperationSymbols()
    op_syms = [str(o) for o in op_syms]
    
    # none are there, so can't construct one from the other
    if not ('join' in op_syms or 'meet' in op_syms):
        raise Exception("Either join or meet needs to be defined.")
        
    if 'join' in op_syms:
        join = alg.getOperation(OperationSymbol('join',2))
        return lambda args: join.intValueAt(args) == args[1]
    else:
        meet = alg.getOperation(OperationSymbol('meet',2))
        return lambda args: meet.intValueAt(args) == args[0]
        
def semi_lattice_minimal(alg):
    alg_leq = semi_lattice_leq(alg)
    universe = list(alg.universe())
    zero = universe[0]
    for i in universe[1:]:
        if alg_leq([i,zero]):
            zero = i
    return zero
    
def semi_lattice_maximal(alg):
    alg_leq = semi_lattice_leq(alg)
    universe = list(alg.universe())
    one = universe[0]
    for i in universe[1:]:
        if alg_leq([one,i]):
            one = i
    return one
    

    
def add_arrow_residuation(alg,fusion_sym='dot'):
    op_syms = alg.similarityType().getOperationSymbols()
    ops = []
    for op in op_syms:
        ops.append(alg.getOperation(op))
    op_syms = [str(o) for o in op_syms]
    
    # already there
    if 'arrow' in op_syms:
        return alg
        
    # assume neg is an involution to construct dual operation
    if 'neg' in op_syms:
        term = Terms.stringToTerm('neg({}(x,neg(y)))'.format(fusion_sym))
        op = TermOperationImp('arrow',term,[Variable.x,Variable.y],alg)
    else:
        alg_leq = semi_lattice_leq(alg)
        alg = add_dual_lattice_operation(alg)
        zero = semi_lattice_minimal(alg)
        
        fusion = alg.getOperation(OperationSymbol(fusion_sym,2))
        join = alg.getOperation(OperationSymbol('join',2))
        class arrow_op(AbstractOperation):
            def intValueAt(self,args):
                x,z = args
                
                # sanity check
                if not alg_leq([fusion.intValueAt([x,zero]),z]):
                    raise Exception("Zero must absorb to have residuation")
                current_best = zero
                for y in alg.universe():
                    if alg_leq([fusion.intValueAt([x,y]),z]):
                        new_best = join.intValueAt([current_best,y])
                        # check
                        if new_best != current_best or new_best != y:
                            if not alg_leq([fusion.intValueAt([x,new_best]),z]):
                                raise Exception("No residuation as {},{} <= {}->{} but {}v{}={} is not.".format(current_best,y,x,z,current_best,y,new_best))
                        current_best = new_best
                        
                return current_best
        
        op = arrow_op("arrow", 2, alg.cardinality())
    
    ops.append(op)
    new_alg = BasicAlgebra(alg.getName(), alg.cardinality(), ops)
    return new_alg
    
    
def add_dot_residuation(alg,arrow_sym='arrow'):
    op_syms = alg.similarityType().getOperationSymbols()
    ops = []
    for op in op_syms:
        ops.append(alg.getOperation(op))
    op_syms = [str(o) for o in op_syms]
    
    # already there
    if 'dot' in op_syms:
        return alg
        
    # assume neg is an involution to construct dual operation
    if 'neg' in op_syms:
        term = Terms.stringToTerm('neg({}(x,neg(y)))'.format(arrow_sym))
        op = TermOperationImp('dot',term,[Variable.x,Variable.y],alg)
    else:
        alg_leq = semi_lattice_leq(alg)
        alg = add_dual_lattice_operation(alg)
        top = semi_lattice_maximal(alg)
        
        arrow = alg.getOperation(OperationSymbol(arrow_sym,2))
        meet = alg.getOperation(OperationSymbol('meet',2))
        class dot_op(AbstractOperation):
            def intValueAt(self,args):
                x,z = args
                
                # sanity check
                if not alg_leq([z,arrow.intValueAt([x,top])]):
                    raise Exception("Arrow must absorb top to have fusion")
                current_best = top
                for y in alg.universe():
                    if alg_leq([z,arrow.intValueAt([x,y])]):
                        new_best = meet.intValueAt([current_best,y])
                        # check
                        if new_best != current_best or new_best != y:
                            if not alg_leq([z,arrow.intValueAt([x,new_best])]):
                                raise Exception("No fusion as {} <= {}->{},{}->{} but {} <=! {}->({}^{}={}).".format(z,x,current_best,x,y,z,x,current_best,y,new_best))
                        current_best = new_best
                        
                return current_best
        
        op = dot_op("dot", 2, alg.cardinality())
    
    ops.append(op)
    new_alg = BasicAlgebra(alg.getName(), alg.cardinality(), ops)
    return new_alg
    
def add_dual_residuation_operation(alg,fusion_sym='dot'):
    op_syms = alg.similarityType().getOperationSymbols()
    ops = []
    for op in op_syms:
        ops.append(alg.getOperation(op))
    op_syms = [str(o) for o in op_syms]
    
    # both already there
    if fusion_sym in op_syms and 'arrow' in op_syms:
        return alg
    if fusion_sym in op_syms:
        return add_arrow_residuation(alg,fusion_sym=fusion_sym)
    if 'arrow' in op_syms:
        return add_dot_residuation(alg)
    # can't
    return alg
    
def check_simple_chain(alg):
    for eq in simple_chain_axioms:
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            the_list = set([result[key] for key in result])
            return sorted(list(the_list))
    return False

def check_dmm(alg,example=True):
    for eq in dmm_axioms:
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            if example:
                print "{} is not a De Morgan monoid as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
            return False
    return True

def check_m(alg,example=True):
    for eq in m_axioms:
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            if example:
                print "{} is not in M as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
            return False
    return True
    
def check_dunn(alg,example=True):
    for eq in dunn_axioms:
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            if example:
                print "{} is not a Dunn monoid as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
            return False
    return True
    
def check_crl(alg,example=True):
    for eq in crl_axioms:
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            if example:
                print "{} is not a crl as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
            return False
    return True
    
def check_brouwerian(alg,example=True):
    op_syms = alg.similarityType().getOperationSymbols()
    ops = []
    for op in op_syms:
        ops.append(alg.getOperation(op))
    op_syms = [str(o) for o in op_syms]
    
    # define dot equal to meet if needed
    if not 'dot' in op_syms:
        term = Terms.stringToTerm('meet(x,y)')
        op = TermOperationImp('dot',term,[Variable.x,Variable.y],alg)
        ops.append(op)
        alg = BasicAlgebra(alg.getName(), alg.cardinality(), ops)
        
    for eq in brouwerian_axioms:
        result = eq.findFailureMap(alg)
        if result:
            l = eq.leftSide()
            r = eq.rightSide()
            if example:
                print "{} is not a Brouwerian algebra as {}={} fails at {}.".format(alg.getName(),make_readable(l),make_readable(r),result)
            return False
    return True
    
def check_heyting(alg,example=True):
    
    # check bot manually for now
    bot = alg.getOperation(OperationSymbol('bot',0))
    bot_el = bot.intValueAt([])
    alg_leq = semi_lattice_leq(alg)
    for i in alg.universe():
        if not alg_leq([bot_el,i]):
            if example:
                print "{} is not a heyting algebra as bot in not below {}.".format(alg.getName(),i)
            return False
    
    return check_brouwerian(alg,example)
    
def get_lattice(alg):
    join = alg.getOperation(OperationSymbol("join",2))
    if join:
        lattice = Lattices.latticeFromJoin(alg.getName(),join)
    else:
        #TODO check what this does to order and elements and zero and underlying universe
        print "Building lattice from meet"
        meet = alg.getOperation(OperationSymbol("meet",2))
        if meet:
            lattice = Lattices.latticeFromMeet(alg.getName(),meet)
        else:
            raise Exception("Algebra needs a join or meet operation to build lattice.")
            
    return lattice

if __name__ == '__main__':
    dir = 'input'
    name = sys.argv[1]
    alg_file_name = os.path.join(dir,"{}.ua".format(name))
    if not os.path.isfile(alg_file_name):
        raise Exception("Could not find: {}".format(alg_file_name))

    alg = AlgebraIO.readAlgebraFile(alg_file_name)

    # Add arrow and meet if not already there
    if check_type(alg):
        if not check_full(alg):
            alg = add_missing_ops(alg)
            print "Added missing operations for {}.".format(alg.getName())
            AlgebraIO.writeAlgebraFile(alg, alg_file_name)
    else:
        raise Exception("Not a dmm type.")
        
    # check that algebra is a dmm
    if check_dmm(alg):
        print "{} is a De Morgan monoid.".format(alg.getName())
    
