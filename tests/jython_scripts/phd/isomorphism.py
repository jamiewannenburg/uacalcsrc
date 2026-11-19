# CPython harness: copied from Jamie's PhD tree (read-only); path roots are relative to this file.
# Changes: none to logic; inputs live under tests/jython_scripts/phd/input/.
import itertools
import sys
sys.path.append("uacalc.jar")

from org.uacalc.alg.op import AbstractOperation

def get_inv_mapping(iso):
    inv_iso = {}
    for i,val in iso.iteritems():
        inv_iso[val] = i
    return inv_iso

def check_isomorphism(alg1,alg2,iso,display=False):
    
    inv_iso = get_inv_mapping(iso)
    
    for i,val in iso.iteritems():
        inv_iso[val] = i

    for op in alg1.operations():
        class new_op_class(AbstractOperation):
            def intValueAt(self,args):
                old_args = [inv_iso[i] for i in args]
                return iso[op.intValueAt(old_args)]
                
        new_op = new_op_class('new_op', op.arity(), alg1.cardinality())
        op2 = alg2.getOperation(op.symbol())
        for tup in itertools.product(range(alg1.cardinality()),repeat=op.arity()):
            if new_op.intValueAt(tup) != op2.intValueAt(tup):
                if (display):
                    print "{}: at {}, {} != {}.".format(op.symbol(),tup,new_op.intValueAt(tup),op2.intValueAt(tup))
                return False
                
    return True
    
def is_isomorphic(alg1,alg2,display=False):
    if alg2.cardinality() != alg1.cardinality():
        if display:
            print "Cardinality of algebras is not the same, so no isomorphism."
        return False
    else:
        univ1 = set(range(alg1.cardinality()))
        univ2 = set(range(alg2.cardinality()))
        # make map forced by constant operations
        constant_map = {}
        zerogen1 = set([])
        zerogen2 = set([])
        for const1 in alg1.constantOperations():
            const2 = alg2.getOperation(const1.symbol())
            a1 = const1.intValueAt([])
            a2 = const2.intValueAt([])
            constant_map[a1] = a2
            zerogen1.add(a1)
            zerogen2.add(a2)
        
        is_subalgebra = False
        while not is_subalgebra:
            new_zerogen = zerogen1.copy()
            for op1 in alg1.operations():
                if op1.arity() != 0:
                    op2 = alg2.getOperation(op1.symbol())
                    for tup in itertools.product(zerogen1,repeat=op1.arity()):
                        tup_map = [constant_map[i] for i in tup]
                        a1 = op1.intValueAt(tup)
                        a2 = op2.intValueAt(tup_map)
                        constant_map[a1] = a2
                        new_zerogen.add(a1)
                        zerogen2.add(a2)
            if zerogen1 < new_zerogen:
                zerogen1 = new_zerogen
            else:
                is_subalgebra = True
                
        rest1 = list(univ1 - zerogen1)
        rest2 = list(univ2 - zerogen2)
        for iso_tup in itertools.permutations(rest1):
            iso = {}
            for i in constant_map:
                iso[i] = constant_map[i]
            for i,val in enumerate(iso_tup):
                iso[val] = rest2[i]
                
            if check_isomorphism(alg1,alg2,iso,display):
                if (display):
                    print "yes, {} is an isomorphism.".format(iso)
                return True
        return False
        