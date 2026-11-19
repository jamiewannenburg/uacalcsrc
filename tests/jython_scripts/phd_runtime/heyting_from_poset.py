
from dmm import AbstractOperation, OperationSymbol, BasicAlgebra, add_arrow_residuation, semi_lattice_maximal, semi_lattice_minimal, check_heyting
from posets import get_upsets_lattice

def heyting_from_poset(po):
    lattice = get_upsets_lattice(po)
    join = lattice.getOperation(OperationSymbol("join",2))
    meet = lattice.getOperation(OperationSymbol("meet",2))
    class e_op(AbstractOperation):
        def intValueAt(self,args):
            return semi_lattice_maximal(lattice)
    e = e_op("e", 0, lattice.cardinality())

    class bot_op(AbstractOperation):
        def intValueAt(self,args):              
            return semi_lattice_minimal(lattice)
    bot = bot_op("bot", 0, lattice.cardinality())

    alg = BasicAlgebra(lattice.getName()+"_*", lattice.cardinality(), [join,meet,e,bot])

    alg = add_arrow_residuation(alg,fusion_sym = 'meet')
    
    return alg

if __name__ == '__main__':
    import sys
    import os
    from posets import InputPoset
    from dmm import AlgebraIO
    
    dir = 'input'
    name = sys.argv[1]
    po_file_name = os.path.join(dir,"{}.lat".format(name))
    if not os.path.isfile(po_file_name):
        raise Exception("Could not find: {}".format(po_file_name))
    alg_file_name = os.path.join(dir,"{}_dual.ua".format(name))

    po = InputPoset(po_file_name)
    
    alg = heyting_from_poset(po)

    # write in complete signature
    AlgebraIO.writeAlgebraFile(alg, alg_file_name)

    if check_heyting(alg):
        print "{} is a Heyting algebra".format(alg.getName())