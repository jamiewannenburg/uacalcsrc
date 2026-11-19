# find info at http://www.latdraw.org/doc/

from dmm import *
from org.latdraw.orderedset import OrderedSet, InputLattice
from itertools import chain, combinations

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def get_upsets_lattice(po):
    # get the universe of the dual
    univ = po.univ()
    filters = []
    for i in univ:
        filters.append(set(i.filter()))
    new_universe = []
    for els in powerset(univ):
        union = set()
        for el in els:
            union.update(set(el.filter()))
        
        found = False
        for new_el in new_universe:
            if new_el == union:
                found = True
                break
        if not found:
            new_universe.append(union)
            
    # print new_universe
    cardinality = len(new_universe)
    
    # now define the new lattice meet and join as intersection and union
    class join_op(AbstractOperation):
        def intValueAt(self,args):
            union = new_universe[args[0]].union(new_universe[args[1]])
            for i,el in enumerate(new_universe):
                if el == union:
                    return i
            raise Exception("Could not find union of {} and {}".format(new_universe[args[0]],new_universe[args[1]]))
            
    join = join_op("join", 2, cardinality)
    
    class meet_op(AbstractOperation):
        def intValueAt(self,args):
            intersection = new_universe[args[0]].intersection(new_universe[args[1]])
            for i,el in enumerate(new_universe):
                if el == intersection:
                    return i
            raise Exception("Could not find intersection of {} and {}".format(new_universe[args[0]],new_universe[args[1]]))
            
    meet = meet_op("meet", 2, cardinality)
    
    return BasicAlgebra('dual({})'.format(po.name), cardinality, [join,meet])
    
    # return Lattices.latticeFromJoin("dual({})".format(po.name), join)

def InputPoset(filename):
    lat_file = InputLattice(filename)
    return OrderedSet.orderedSetFromFilters(lat_file.name, lat_file.labels, lat_file.upperCoversList)
    
def PosetToLatFile(po):
    po_str = "({}\n".format(po.getName())
    
    for el in po.univ():
        po_str = " (({} ({}))\n".format(el.label(),' '.join([e.label() for e in el.filter()]))
    
    po_str = ")"
    return po_str
    
def dict2poset(d,name):
    labels = sorted(d.keys())
    filters = []
    for n in labels:
        if isinstance(d[n],set):
            filters.append(sorted(list(d[n])))
        else:
            filters.append(d[n])
    return OrderedSet.orderedSetFromFilters(name, labels, filters)
    
if __name__ == '__main__':
    # draw poset
    from latex import get_graph_from_poset
    
    import os
    import sys
    import json

    in_dir = 'input'
    out_dir = 'output'
    
    name = sys.argv[1]
    po_file_name = os.path.join(in_dir,"{}.lat".format(name))
    if not os.path.isfile(po_file_name):
        raise Exception("Could not find: {}".format(po_file_name))

    
    po = InputPoset(po_file_name)
    graph_file_name = os.path.join(out_dir,name+".json")
    pdf_file_name = os.path.join(out_dir,name+".pdf")
    # tex_file_name = os.path.join(out_dir,name+".tex")
    
    
    # make drawing
    graph_dict = get_graph_from_poset(po)
    
    with open(graph_file_name,'w') as f:
        json.dump( graph_dict, f )
    os.system('python draw.py {}'.format(graph_file_name))
    # os.system(pdf_file_name)
    