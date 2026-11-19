from itertools import chain, combinations
import sys

def gen_powerset(gs):
    for r in range(len(gs)+1):
        for t in combinations(gs,r):
            yield t
    
def powerset(gs):
    p = []
    for t in gen_powerset(gs):
        p.append(t)
    return p
    
def intersection(t1,t2):
    return tuple(item for item in t1 if item in t2)
    
def complement(t,gs):
    return tuple(item for item in tuple(gs) if item not in t)
    
def get_bottom(meet):
    for row in meet:
        first = row[0]
        const = True
        for col in row:
            if col != first:
                const = False
                break
        if const:
            return first
            
def get_bottom_np(meet):
    l1,l2 = meet.shape
    assert l1==l2
    for i in range(l1):
        row = meet[i,:]
        if (row == row[0]).all():
            return row[0]
            
def get_atoms(meet,bot):
    atoms = []
    for row in meet:
        at = True
        other = bot
        for col in row:
            if col!=bot:
                if col != other:
                    if other == bot:
                        other = col
                    else:
                        at = False
                        break
        if at and other!=bot:
            atoms.append(other)
    return atoms
    
def get_atoms_np(meet,bot):
    l1,l2 = meet.shape
    assert l1==l2
    atoms = []
    for i in range(l1):
        row = meet[i,:]
        nonbot = row[row!=bot]
        if len(nonbot)>0 and (nonbot==nonbot[0]).all():
            atoms.append(nonbot[0])
    return atoms
    
def get_join(meet,neg):
    l = len(meet[0])
    join = []
    for x in range(l):
        jrow = []
        for y in range(l):
            negx = neg[x]
            negy = neg[y]
            jrow.append(neg[meet[negx][negy]])
        join.append(jrow)
    return join
    
def get_join_np(meet,neg):
    # x v y = ~(~x^~y)
    return neg[meet[neg,:][:,neg]]
            
def gen_joins(join,atoms,bot):
    for t in gen_powerset(atoms):
        j = bot
        for at in t:
            j = join[j][at]
        yield j
    
def get_maps(join,atoms,bot):
    #at2g = {at:i for i,at in enumerate(atoms)}
    n=len(atoms)
    gs = list(range(n))
    i_to_p = {}
    p_to_i = {}
    
    # powerset
    for r in range(n+1):
        for t in combinations(gs,r):
            j = bot
            for i in t:
                j = join[j][atoms[i]]
            i_to_p[j]=t
            p_to_i[t]=j
    return i_to_p,p_to_i

def get_maps_np(join,atoms,bot):
    #at2g = {at:i for i,at in enumerate(atoms)}
    n=len(atoms)
    gs = list(range(n))
    i_to_p = {}
    p_to_i = {}
    
    # powerset
    for r in range(n+1):
        for t in combinations(gs,r):
            j = bot
            for i in t:
                j = join[j,atoms[i]]
            i_to_p[j]=t
            p_to_i[t]=j
    return i_to_p,p_to_i

def psalg(gs):
    p = powerset(gs)
    p_to_i = {x:i for i,x in enumerate(p)}
    meet = []
    for x in p:
        row = []
        for y in p:
            row.append(intersection(x,y))
        meet.append(row)
    neg = []
    for x in p:
        neg.append(complement(x,gs))
    return p,{'^':meet,'~':neg}
    
def psalg_to_int(p,alg):
    u = list(range(len(p)))
    p_to_i = {x:i for i,x in enumerate(p)}
    # meet
    meet = []
    for row in alg['^']:
        nrow = []
        for col in row:
            nrow.append(p_to_i[col])
        meet.append(nrow)
    # neg
    neg = []
    for n in alg['~']:
        neg.append(p_to_i[n])
        
    return u,{'^':meet,'~':neg}
    
def alg_to_clauses(u,alg):
    clauses = []
    for i,row in enumerate(alg['^']):
        x = u[i]
        for j,col in enumerate(row):
            y = u[j]
            clauses.append(f"{x} ^ {y} = {col}.")
    for i,v in enumerate(alg['~']):
        clauses.append(f"~({u[i]}) = {v}.")
    return clauses

if __name__=="__main__":
    try:
        ngenerators = int(sys.argv[1])
    except Exception:
        print("Usage: python powerset.py ngenerators")
        print("Assuming ngenerators is 1")
        ngenerators = 1
    gs = list(range(ngenerators))
    p,palg = psalg(gs)
    u,alg = psalg_to_int(p,palg)
    clauses = alg_to_clauses(u,alg)
    for c in clauses:
        print(c)
        
    # given alg can I reconstruct palg?
    bot = get_bottom(alg['^'])
    assert bot==u[0]
    atoms = get_atoms(alg['^'],bot)
    assert atoms==u[1:ngenerators+1]
    join = get_join(alg['^'],alg['~'])
    i_to_p,p_to_i = get_maps(join,atoms,bot)
    # check elements map
    for i,x in enumerate(p):
        assert i == p_to_i[x]
        assert x == i_to_p[i]
    # check operations map
    for i in range(len(p)):
        for j in range(len(p)):
            assert i_to_p[alg['^'][i][j]] == palg['^'][i][j]
            assert p_to_i[palg['^'][i][j]] == alg['^'][i][j]
    for i in range(len(p)):
        assert i_to_p[alg['~'][i]] == palg['~'][i]
        assert p_to_i[palg['~'][i]] == alg['~'][i]
            
    try:
        import numpy as np
        meet = np.array(alg['^'])
        neg = np.array(alg['~'])
        botn = get_bottom_np(meet)
        assert botn == bot
        atomsn = get_atoms_np(meet,botn)
        assert atomsn==atoms
        joinn = get_join_np(meet,neg)
        assert (joinn == np.array(join)).all()
        i_to_pn,p_to_in = get_maps_np(joinn,atoms,bot)
        for i,x in enumerate(p):
            assert i_to_pn[i] == i_to_p[i]
            assert p_to_in[x] == p_to_i[x]
        
    except ImportError:
        print("No numpy available.")
