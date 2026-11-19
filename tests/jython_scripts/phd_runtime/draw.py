import pygraphviz as pgv

def graph_from_dict(dic):
    G=pgv.AGraph('digraph G {ratio="fill";size="5,4";rankdir="BT";}')
    #ratio="fill";size="7.267,10.692"A0:"33.1,46.8"A4:"11.7,8.3";rankdir="LR""BT";ranksep=.75;overlap=false;
    G.graph_attr['label']=' '
    G.graph_attr['tooltip']=' '

    G.add_nodes_from(dic['nodes'])
    G.add_edges_from(dic['edges'])
    
    if 'labels' in dic and len(dic['labels']) == len(dic['nodes']):
        for n in dic['nodes']:
            node = G.get_node(n)
            node.attr['label'] = dic['labels'][n]
    
    return G
    
if __name__=='__main__':
    import os
    import sys
    import json

    graph_file_name = sys.argv[1]
    if not os.path.isfile(graph_file_name):
        raise Exception("Could not find: {}".format(graph_file_name))
        
    graph_file = graph_file_name.replace('.json','')
    with open(graph_file_name,'r') as f:
        graph_dict = json.load(f)
        
    G = graph_from_dict(graph_dict)
    G.write(graph_file + '.dot')
    
    # G1.draw(graph_file + '.svg',format="svg",prog='fdp')
    G.draw(graph_file + '.pdf',format="pdf",prog='dot')#['neato'|'dot'|'twopi'|'circo'|'fdp'|'sfdp'|'nop']
    # os.system(out_pdf_file)