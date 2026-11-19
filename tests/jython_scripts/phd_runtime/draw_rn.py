import pygraphviz as pgv
import networkx as nx

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
    import re
    import matplotlib.pyplot as plt
    
    graph_file_name = sys.argv[1]
    if not os.path.isfile(graph_file_name):
        raise Exception("Could not find: {}".format(graph_file_name))
        
    graph_file = graph_file_name.replace('.json','')
    with open(graph_file_name,'r') as f:
        graph_dict = json.load(f)
        
    G = graph_from_dict(graph_dict)
    
    # N = nx.Graph(G)
    # nodes = []
    # for n in N:
        # if not int(re.sub('w','',n))%2:
            # nodes.append(n)
    # pos = nx.bipartite_layout(N, nodes, scale=0.5)
    
    # f = plt.figure()
    # nx.draw(N, pos, node_color='w', node_size=1500, font_size=25, with_labels=True)
    # f.savefig(graph_file+".pdf", bbox_inches='tight')
    # # plt.show()
    
    
    # Even = pgv.AGraph()
    # Odd = pgv.AGraph()
    even_nodes = []
    odd_nodes = []
    for n in G.iternodes():
        if int(re.sub('w','',n))%2:
            # Odd.add_node(n)
            odd_nodes.append(n)
        else:
            # Even.add_node(n)
            even_nodes.append(n)
            
    if len(even_nodes)>0 and len(odd_nodes)>0:
        Odd = G.add_subgraph(nbunch=odd_nodes, name='odd')
        # w1 = Odd.get_node('w1')
        # w1.attr['pos']='4,0!'
        # Odd.add_node('left',pos="0,0")#,style="invis"
        # # Odd.add_edge('left','w0',style="invis")
        # for n in Odd.iternodes():
            # Odd.add_edge('left',n,style="invis")
        Even = G.add_subgraph(nbunch=even_nodes, name='even')
        # w0 = Even.get_node('w0')
        # w0.attr['pos']='0,0!'
        # Even.add_node('right',pos="4,0")#,style="invis"
        # # Even.add_edge('right','w1',style="invis")
        # for n in Even.iternodes():
            # Even.add_edge('right',n,style="invis")
        
        
        # other_edges = []
        for e in G.edges_iter():
            if Even.has_edge(e[0], e[1]):
                pass
            elif Odd.has_edge(e[0], e[1]):
                pass
            else:
                e.attr['constraint']=False
    
    # print(Odd.to_string())
    # print(Even.to_string())
    # print(G.to_string())
    
    G.write(graph_file + '.dot')
    
    # G1.draw(graph_file + '.svg',format="svg",prog='fdp')
    G.draw(graph_file + '.pdf',format="pdf",prog='dot')#['neato'|'dot'|'twopi'|'circo'|'fdp'|'sfdp'|'nop']
    # os.system(graph_file + '.pdf')