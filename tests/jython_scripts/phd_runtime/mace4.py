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

# from functools import reduce 
# from operator import mul
# def reshape(lst, shape):
    # if len(shape) == 1:
        # return lst
    # n = reduce(mul, shape[1:])
    # return [reshape(lst[i*n:(i+1)*n], shape[1:]) for i in range(len(lst)//n)]

convert_dict = {
    'prover9': {
        'v':'join',
        '+':'join',
        '~':'neg',
        '*':'dot',
        'e':'e',
        '^':'meet',
        '\\':'arrow',
        '/':'rarrow',
        "'":'star',
    }
}

def translate(op,translation='prover9'):
    try:
        return convert_dict[translation][op]
    except KeyError:
        return op


import pyparsing as pp

operation_table = pp.Suppress('[')+pp.delimitedList(pp.Word(pp.nums),delim=',')+pp.Suppress(']')
operation_table.setParseAction(lambda s,l,t: [[int(x) for x in t]])
arity= pp.Word(pp.alphanums+'<>*=-~!\\/:+^$:;\'?')+pp.ZeroOrMore(pp.Suppress('(')+pp.delimitedList(pp.Word('_'),delim=',')+pp.Suppress(')'))
arity.setParseAction(lambda s,l,t: {'name':t[0],'arity':len(t)-1})
relation = 'relation'+pp.Suppress('(')+ arity +pp.Suppress(',')+ operation_table +pp.Suppress(')')
function = 'function'+pp.Suppress('(')+ arity +pp.Suppress(',')+ operation_table +pp.Suppress(')')

# Build operation
def _func_and_relation_parser(s,l,t):
    if t[0] == 'relation':
        return False
    
    op_len = len(t[2])
    arity = t[1]['arity']
    name = translate(t[1]['name'])
    
    if arity == 0:
        class op(AbstractOperation):
            def intValueAt(self,args):
                return t[2][0]
        op_fun = op(name,arity,1)
    else:
        cardinality = int(op_len**(1./arity))
        class op(AbstractOperation):
            def intValueAt(self,args):
                return t[2][sum((cardinality**(i))*args[arity-i-1] for i in range(arity))]
    
        op_fun = op(name,arity,cardinality)
    return op_fun
relation.setParseAction(_func_and_relation_parser)
function.setParseAction(_func_and_relation_parser)

operations = pp.Suppress('[')+ pp.delimitedList(relation|function,delim=',')+pp.Suppress(']')
operations.setParseAction(lambda s,l,t: [[x for x in t if x]])
number = 'number = '+pp.Word(pp.nums)
number.setParseAction(lambda s,l,t: {'number':t[1]})
seconds = 'seconds = '+pp.Word(pp.nums)
seconds.setParseAction(lambda s,l,t: {'seconds':t[1]})
meta = pp.Suppress('[')+ number +pp.Suppress(',')+ seconds +pp.Suppress(']')
meta.setParseAction(lambda s,l,t: {k:v for x in t for k,v in x.items()})
cardinality = pp.Word(pp.nums)
cardinality.setParseAction(lambda s,l,t: int(t[0]))

interpretation = 'interpretation'+pp.Suppress('(')+ cardinality +pp.Suppress(',')+ meta +pp.Suppress(',')+ operations +pp.Suppress(').')
interpretation.ignore('%' + pp.restOfLine)
# Build algebra
def _interpretation_parser(s,l,t):
    cardinality = t[1]
    number = t[2]['number']
    ops = t[3]
    alg = BasicAlgebra("S_{%d}^{%s}"%(cardinality,number), cardinality, ops)
    alg = BasicAlgebra("S_{%d}^{%s}"%(cardinality,number), cardinality, ops)
    dot = alg.getOperation(OperationSymbol("dot",2))
    # alg_file_name = os.path.join(dir,"S-%d-%s.ua"%(cardinality,number))
    # AlgebraIO.writeAlgebraFile(alg, alg_file_name)
    return alg
interpretation.setParseAction(_interpretation_parser)
model = pp.ZeroOrMore(interpretation)
model.ignore('%' + pp.restOfLine)
# model.setParseAction(lambda s,l,t: [t])
def _somef(s,l,t):
    return t
model.setParseAction(_somef)

def to_alg_stream(handle):
    # read from handle into a buffer char by char until a period is found
    # so handle can be file or stdin
    buffer = ""
    period_found = False
    comment_found = False
    while True:
        char = handle.read(1)
        if not char: # end of file
            break
        # if period_found or comment_found, ignore the rest of the line
        if period_found or comment_found:
            if char == '\n':
                period_found = False
                comment_found = False
                buffer = ""
        else: # not after a period or comment
            buffer += char
            if char == '.':
                period_found = True
                buffer += char
                yield interpretation.parseString(buffer)[0]
                buffer = ""
            if char == '%':
                comment_found = True
            
def to_alg(mace4_filename):
    with open(mace4_filename) as f:
        for alg in to_alg_stream(f):
            yield alg
    
if __name__=='__main__':
    
    # from dmm import add_dual_lattice_operation

    name = sys.argv[1]
    alg_file_name = "{}.model".format(name)
    if not os.path.isfile(alg_file_name):
        raise Exception("Could not find: {}".format(alg_file_name))
    # to_alg(alg_file_name)
    for i,alg in enumerate(to_alg(alg_file_name)):
        # alg = add_dual_lattice_operation(alg)
        alg_file_name = os.path.join(dir,"%s-%d.ua"%(name,i+1))#alg.cardinality()
        alg.setName("%s^{%d}"%(name,i+1))
        AlgebraIO.writeAlgebraFile(alg, alg_file_name)
        print("Wrote ",alg_file_name)
        