from dmm import translate, get_lattice, OperationSymbol

def get_operation_table(operation, labels=None):
    
    arity = operation.arity()
    if arity >= 3:
        raise Exception("Cannot make tables for operations with arity greater than two.")
        
    op = str(operation.symbol())
    cardinality = operation.getSetSize()
    
    if arity == 0:
        return "\n$${}={}$$\n".format(translate(op,translation='latex'),operation.intValueAt([]))
        
    table_str = "\\begin{tabular}{r|"+'c'*cardinality+"}\n"
    table_str += "${}$ & {} \\\\\n\\hline\n".format( translate(op,translation='latex'), ' & '.join([str(i) for i in range(cardinality)]) )
    if arity == 1:
        table_str += " & {}\n".format( ' & '.join([str(operation.intValueAt(i)) for i in range(cardinality)]) )
    
    else: # arity = 2
        for i in range(cardinality):
            if labels:
                table_str += "${} = $".format(labels[i])
            table_str += "{} & {} \\\\\n".format(i, ' & '.join([str(operation.intValueAt([i,j])) for j in range(cardinality)]) )
            
    table_str += "\\end{tabular}\n\n"
    return table_str
    
def get_graph(alg):
    #TODO add labels to the lattice and check meet for labels?
    lattice = get_lattice(alg)
    return get_graph_from_poset(lattice.getPoset())
    
def get_graph_from_poset(po):
    cardinality = po.card()
    nodes = [str(e) for e in po.univ()]
    edges = []
    for e in po.univ():
        for cover in e.upperCovers():
            edges.append([str(e),str(cover)])
    # bot = po.zero()
    # covers = set([bot])
    # while len(covers) > 0:
        # new_covers = set()
        # for cover in covers:
            # c_covers = cover.upperCovers()
            # for c_cover in c_covers:
                # edges.append([int(str(cover)),int(str(c_cover))])
            
            # new_covers = new_covers | set(c_covers)
        # covers = new_covers
    return {'nodes':nodes,'edges':edges}
    
def get_description(alg, pdf_file_name, scale=1., labels=None):
    tex = "\\includegraphics[scale="+ str(scale) +"]{"+pdf_file_name+"} \n\n"
    
    tex += "\n\n\n\\begin{center}\n\n"
    for op in alg.operations():
        if not str(op.symbol()) in ['meet','join']:
            tex += get_operation_table(op,labels) + '\n\n'
    tex += "\\end{center}\n\n"
        
    return tex
    
def get_dmm_description(alg, pdf_file_name, scale=1., labels=None):
    tex = "\\includegraphics[scale="+ str(scale) +"]{"+pdf_file_name+"} \n\n"
    
    dot = alg.getOperation(OperationSymbol('dot',2))
    arrow = alg.getOperation(OperationSymbol('arrow',2))
    neg = alg.getOperation(OperationSymbol('neg',1))
    e = alg.getOperation(OperationSymbol('e',0))
    
    tex += "\n\n\n\\begin{center}\n\n"
    for op in [e,neg,dot,arrow]:
        tex += get_operation_table(op,labels) + '\n\n'
    tex += "\\end{center}\n\n"
        
    return tex
    
def get_dunn_description(alg, pdf_file_name, scale=1.,labels=None):
    tex = "\\includegraphics[scale="+ str(scale) +"]{"+pdf_file_name+"} \n\n"
    
    dot = alg.getOperation(OperationSymbol('dot',2))
    arrow = alg.getOperation(OperationSymbol('arrow',2))
    e = alg.getOperation(OperationSymbol('e',0))
    
    tex += "\n\n\n\\begin{center}\n\n"
    for op in [e,dot,arrow]:
        tex += get_operation_table(op,labels) + '\n\n'
    tex += "\\end{center}\n\n"
        
    return tex
    
def get_my_description(alg, pdf_file_name, scale=1.,labels=None):
    tex = "\\includegraphics[scale="+ str(scale) +"]{"+pdf_file_name+"} \n\n"
    
    dot = alg.getOperation(OperationSymbol('dot',2))
    arrow = alg.getOperation(OperationSymbol('arrow',2))
    monus = alg.getOperation(OperationSymbol('monus',2))
    e = alg.getOperation(OperationSymbol('e',0))
    
    tex += "\n\n\n\\begin{center}\n\n"
    for op in [e,dot,arrow,monus]:
        tex += get_operation_table(op,labels) + '\n\n'
    tex += "\\end{center}\n\n"
        
    return tex
    
# def get_order(lattice):
    # cardinality = lattice.cardinality()
    # elements = []
    # for i in range(cardinality):
        # elements.append({'rank':0,'col':0})
    
    # bot = lattice.zero()
    # covers = set(bot.upperCovers())
    # rank = 0
    # while len(covers) > 0:
        # new_covers = set()
        # for i,cover in enumerate(covers):
            # elements[int(str(cover))]['rank'] = rank
            # elements[int(str(cover))]['col'] = i
            
            # new_covers = new_covers | set(cover.upperCovers())
        # covers = new_covers
        # rank += 1
    # return elements
    
# def get_drawing(alg, length = 15):
    # join = alg.getOperation(OperationSymbol("join",2))
    # if join:
        # lattice = Lattices.latticeFromJoin(alg.getName(),join)
    # else:
        # meet = alg.getOperation(OperationSymbol("meet",2))
        # if meet:
            # lattice = Lattices.latticeFromMeet(alg.getName(),meet)
        # else:
            # raise Exception("Algebra needs a join or meet operation to build lattice.")
            
    # order = get_order(lattice)
    # print order
    # points

if __name__ == '__main__':
    import os
    import sys
    import json
    from dmm import check_type, check_m, AlgebraIO

    in_dir = 'input'
    out_dir = 'output'
    
    name = sys.argv[1]
    alg_file_name = os.path.join(in_dir,"{}.ua".format(name))
    if not os.path.isfile(alg_file_name):
        raise Exception("Could not find: {}".format(alg_file_name))

    
    alg = AlgebraIO.readAlgebraFile(alg_file_name)
    graph_file_name = os.path.join(out_dir,name+".json")
    pdf_file_name = os.path.join(out_dir,name+".pdf")
    tex_file_name = os.path.join(out_dir,name+".tex")
    
    # check labels
    labels = None
    if len(sys.argv) > 2:
        if len(sys.argv) != alg.cardinality()+2:
            raise Exception("You must add additional arguments equal to cardinality of algebra ({})".format(alg.cardinality()))
        labels = sys.argv[2:]
    
    
    # make drawing
    graph_dict = get_graph(alg)
    
    with open(graph_file_name,'w') as f:
        json.dump( graph_dict, f )
    os.system('python draw.py {}'.format(graph_file_name))
    # os.system(pdf_file_name)
    
    # make text file
    with open(tex_file_name,'w') as f:
        pdf_file_name = pdf_file_name.replace('\\','/')
        tex = "\\begin{center}\n$\\mathbf{%s}$:\n\\end{center}\n\n"%( alg.getName() )
        tex += get_description(alg, pdf_file_name, scale=0.5, labels=labels)
        f.write( tex )
    
