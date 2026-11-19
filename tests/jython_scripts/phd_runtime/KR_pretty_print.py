import sys
import os
import re
from itertools import chain, combinations, product
import numpy as np
import pyparsing as pp
from powerset import psalg, get_bottom_np, get_atoms_np, get_join_np, get_maps_np

dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'output')

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

operation_table = pp.Suppress('[')+pp.delimitedList(pp.Word(pp.nums),delim=',')+pp.Suppress(']')
operation_table.setParseAction(lambda s,l,t: [[int(x) for x in t]])
arity= pp.Word(pp.alphanums+'<>*=-~!\\/:+^$:;\'?')+pp.ZeroOrMore(pp.Suppress('(')+pp.delimitedList(pp.Word('_'),delim=',')+pp.Suppress(')'))
arity.setParseAction(lambda s,l,t: {'name':t[0],'arity':len(t)-1})
relation = 'relation'+pp.Suppress('(')+ arity +pp.Suppress(',')+ operation_table +pp.Suppress(')')
function = 'function'+pp.Suppress('(')+ arity +pp.Suppress(',')+ operation_table +pp.Suppress(')')

# Build operation
def _func_and_relation_parser(s,l,t):
    if t[0] == 'relation':
        # ignore relations
        return False
    
    op_len = len(t[2])
    arity = t[1]['arity']
    name = t[1]['name'] # translate(t[1]['name'])
    
    if arity == 0:
        return name,t[2][0]
    else:
        cardinality = int(op_len**(1./arity))
        #op_table = np.zeros(tuple([cardinality]*arity))
        op_table = np.array(t[2]).reshape(tuple([cardinality]*arity))
    return name, op_table
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
    alg = {'cardinality':cardinality,'number':number}
    for name,op in t[3]:
        alg[name] = op
    return alg
    
interpretation.setParseAction(_interpretation_parser)
model = pp.ZeroOrMore(interpretation)
model.ignore('%' + pp.restOfLine)
# model.setParseAction(lambda s,l,t: [t])
def _somef(s,l,t):
    return t
model.setParseAction(_somef)


def to_alg(mace4_filename):
    with open(mace4_filename) as f:
        s = f.read()
    for alg_str in re.finditer(r'^.*?\.$',s,re.MULTILINE|re.DOTALL):
        if alg_str.group(0)[0] != '%':
            yield interpretation.parseString(alg_str.group(0))[0]
    # return model.parseString(s)
    
def tup2set(tup):
    s = r"$\{"
    s+=', '.join([str(t) for t in tup])
    s+=r"\}$"
    return s
    
def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x
    
if __name__=='__main__':
    
    name = sys.argv[1]
    alg_file_name = "{}.model".format(name)
    if not os.path.isfile(alg_file_name):
        raise Exception("Could not find: {}".format(alg_file_name))
    # to_alg(alg_file_name)
    card = int(re.search(r"\d+",alg_file_name).group(0))
    
    ngen = card.bit_length() - 1
    for i,alg in enumerate(to_alg(alg_file_name)):
        tex_file_name = os.path.join(dir,f"{name}-{i+1}.tex")
        alg_name = f"{name}-{i+1}"
        meet = alg['^']
        neg = alg['~']
        dot = alg['*']
        u = np.arange(alg['cardinality'])
        bot = get_bottom_np(meet)
        aatoms = get_atoms_np(meet,bot)
        assert ngen == len(aatoms)
        
        # put e first
        e = alg['e']
        atoms = aatoms
        # if e in aatoms:
            # atoms = [e]
            # for a in aatoms:
                # if a != e:
                    # atoms.append(a)
        # else:
            # atoms = aatoms
        # # swap so e is first
        # meet[aatoms,:] = meet[atoms,:]
        # meet[:,aatoms] = meet[:,atoms]
        # dot[:,aatoms] = dot[:,atoms]
        # dot[aatoms,:] = dot[atoms,:]
        # neg[aatoms]=neg[atoms]
        join = get_join_np(meet,neg)
        i_to_p,p_to_i = get_maps_np(join,atoms,bot)
        gs = np.arange(len(atoms))
        p,palg = psalg(gs)
        # check ~(e)*~(e) is top
        f = neg[e]
        t = dot[f,f]
        assert (meet[t,:] == u).all()
        # check meet is powerset meet
        for i in range(len(p)):
            for j in range(len(p)):
                assert i_to_p[meet[p_to_i[p[i]],p_to_i[p[j]]]]  ==  palg['^'][i][j]
        for i in range(len(p)):
            assert i_to_p[neg[p_to_i[p[i]]]] == palg['~'][i]
        
        # print operation table of atoms
        s = f"\\textbf{{{alg_name}}}\n\n"
        s += f"$e$={tup2set(i_to_p[e])}\n\n"
        # header
        s += r"\begin{tabular}{"
        s += "l|"+"c"*len(atoms)
        s += "}\n"
        # table header
        for a in atoms:
            s += rf"& {tup2set(i_to_p[a])}"
        s += "\\\\\n\\hline\n"
        # operation table
        for x in atoms:
            s += rf"{tup2set(i_to_p[x])}"
            for y in atoms:
                xdoty = dot[x,y]
                s += rf"& {tup2set(i_to_p[xdoty])}"
            s += "\\\\\n"
            
        s+= r"\end{tabular}"
        with open(tex_file_name,'w') as f:
            f.write(s)
        print("wrote: ",tex_file_name)
        # check that you can reconstruct * from atoms
        for x in p:
            for y in p:
                # (x v y v z) * (a v b v c) =
                # ((x v y v z) * a)v((x v y v z)*b)v((x v y v z)*c) = 
                # (x*a)v(y*a)v(z*a)v(x*b)v(y*b)v(z*b)v(x*c)v(y*c)v(z*c)
                jn = bot
                for i in x:
                    for j in y:
                        jn = join[jn][dot[p_to_i[(i,)]][p_to_i[(j,)]]]
                assert dot[p_to_i[x],p_to_i[y]] == jn