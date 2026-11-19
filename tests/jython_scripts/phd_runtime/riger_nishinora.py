import os
import sys

from posets import dict2poset
from heyting_from_poset import heyting_from_poset

#TODO if needed change so we don't redo things

def principal_upset(n):
    if n==0:
        return {'w0':set([])}
    elif n==1:
        return {'w1':set([])}
    elif n==2:
        filters = principal_upset(0)
        filters['w2'] = set(['w0'])
        return filters
    else:
        name = 'w{}'.format(n)
        n_min_2 = 'w{}'.format(n-2)
        n_min_3 = 'w{}'.format(n-3)
        filters = principal_upset(n-2)
        #union
        filters.update(principal_upset(n-3))
        filter = filters[n_min_2].union(filters[n_min_3])
        filter.add(n_min_2)
        filter.add(n_min_3)
        filters[name] = filter
        return filters
        
def upsets(limit=None):
    i = 0
    while limit == None or i < limit:
        # 2i
        twoi = principal_upset(2*i)
        yield twoi
        # 2i+1
        twoip1 = principal_upset(2*i+1)
        yield twoip1
        # 2i, 2i+1
        twoi.update(twoip1)
        yield twoi
        # 2i+2, 2i+1
        twoip1.update(principal_upset(2*i+2))
        yield twoip1
        
        i = i+1
        
def posets(limit=None):
    for j,d in enumerate(upsets(limit=limit)):
        i = j/4
        if j%4 == 0:
            yield dict2poset(d,'RN({})'.format(2*i))
        elif j%4 == 1:
            yield dict2poset(d,'RN({})'.format(2*i+1))
        elif j%4 == 2:
            yield dict2poset(d,'RN({},{})'.format(2*i,2*i+1))
        elif j%4 == 3:
            yield dict2poset(d,'RN({},{})'.format(2*i+2,2*i+1))
    
def latex_picture(level):
    length = 12
    r_text_offset_x = 6
    l_text_offset_x = 45
    text_offset_y = 2
    y_offset = 5
    width = 2*l_text_offset_x+3*length
    height = 2*y_offset + 2*length*level
    bot_x = l_text_offset_x+2*length
    tex = """
\\begin{{picture}}({width},{height})
%
%% RN
%
\\put({bot_x},{bot_y}){{\\circle*{{4}}}}
\\put({bot_x},{bot_y}){{\\line(1,1){{{length}}}}}
\\put({bot_x},{bot_y}){{\\line(-1,1){{{length}}}}}
\\put({r_x},{y}){{\\circle*{{4}}}}
\\put({r_x},{y}){{\\line(-1,1){{{length}}}}}
\\put({l_x},{y}){{\\circle*{{4}}}}
\\put({l_x},{y}){{\\line(1,1){{{length}}}}}
\\put({bot_x},{t_y}){{\\circle*{{4}}}}
\\put({bot_x_t},{bot_y_t}){{$\\bot$}}
\\put({l_x_t},{y_t}){{$w_0$}}
\\put({r_x_t},{y_t}){{$w_1$}}
\\put({bot_x_t},{t_y_t}){{$a_1$}}


    """.format(
    width = width,
    height = height,
    length = length,
    bot_x = bot_x,
    bot_y = y_offset,
    l_x = bot_x-length,
    r_x = bot_x+length,
    y = y_offset + length,
    t_y = y_offset + 2*length,
    bot_x_t = bot_x+r_text_offset_x,
    bot_y_t = y_offset-text_offset_y,
    l_x_t = bot_x-length+r_text_offset_x,
    r_x_t = bot_x+length+r_text_offset_x,
    y_t = y_offset + length-text_offset_y,
    t_y_t = y_offset + 2*length-text_offset_y
    )
    
    for i in range(1,level):
        tex += """
\\put(0,{bot_y_t}){{$w_{{{w_l}}}$}}
\\put({ll_x},{bot_y}){{\\circle*{{4}}}}
\\put({ll_x},{bot_y}){{\\line(1,1){{{length}}}}}
\\put({ll_x},{bot_y}){{\\line(1,-1){{{length}}}}}
\\put({l_x_t},{y_t}){{$a_{{{w_l}}}$}}
\\put({l_x},{y}){{\\circle*{{4}}}}
\\put({l_x},{y}){{\\line(1,-1){{{length}}}}}

\\put({l_x},{y}){{\\line(1,1){{{length}}}}}
\\put({r_x_t},{y_t}){{$w_{{{w_r}}}$}}
\\put({r_x},{y}){{\\circle*{{4}}}}
\\put({r_x},{y}){{\\line(-1,1){{{length}}}}}
\\put({r_x},{y}){{\\line(-1,-1){{{length}}}}}
\\put({bot_x_t},{t_y_t}){{$a_{{{w_r}}}$}}
\\put({bot_x},{t_y}){{\\circle*{{4}}}}

        """.format(
        length = length,
        w_l = i*2,
        w_r = i*2+1,
        ll_x = bot_x - 2*length,
        l_x = bot_x - length,
        bot_x = bot_x,
        r_x = bot_x + length,
        l_x_t = bot_x - length + r_text_offset_x,
        bot_x_t = bot_x + r_text_offset_x,
        r_x_t = bot_x + length + r_text_offset_x,
        bot_y = y_offset + 2*i*length,
        y = y_offset + 2*i*length + length,
        t_y = y_offset + 2*i*length + 2*length,
        bot_y_t = y_offset + 2*i*length - text_offset_y,
        y_t = y_offset + 2*i*length + length - text_offset_y,
        t_y_t = y_offset + 2*i*length + 2*length - text_offset_y
        )
    tex += "\n\\end{picture}"
    return tex


if __name__ == '__main__':
    import os
    from dmm import AlgebraIO
    from latex import get_graph_from_poset, get_graph
    from posets import PosetToLatFile
    import json
    
    dir = 'input'
    out_dir = 'output'
    scale = 0.5
    
    tex_file_name = "RN.tex"
    tex = ""
    
    print(latex_picture(7))
    
    # for j,po in enumerate(posets(limit=5)):
        # i = j/4
        # if j%4 == 0:
            # name = 'RN-{}'.format(2*i)
            # upset = "\\{w_{%s}\\}"%(2*i)
        # elif j%4 == 1:
            # name = 'RN-{}'.format(2*i+1)
            # upset = "\\{w_{%s}\\}"%(2*i+1)
        # elif j%4 == 2:
            # name = 'RN-{}-{}'.format(2*i,2*i+1)
            # upset = "\\{w_{%s},w_{%s}\\}"%(2*i,2*i+1)
        # elif j%4 == 3:
            # name = 'RN-{}-{}'.format(2*i+2,2*i+1)
            # upset = "\\{w_{%s},w_{%s}\\}"%(2*i+2,2*i+1)
            
        # # write po
        # po_file_name = os.path.join(dir,"{}.lat".format(name))
        # graph_file_name = os.path.join(out_dir,name+".json")
        # po_pdf_file_name = out_dir+'/'+name+".pdf"
        
        # with open(po_file_name,'w') as f:
            # f.write(PosetToLatFile(po))
        
        # graph_dict = get_graph_from_poset(po)
        # with open(graph_file_name,'w') as f:
            # json.dump( graph_dict, f )
        # os.system('python draw_rn.py {}'.format(graph_file_name))
        
        # # write heyting algebra
        # alg_file_name = os.path.join(dir,"{}_dual.ua".format(name))
        # graph_file_name = os.path.join(out_dir,name+"_dual.json")
        # alg_pdf_file_name = out_dir+'/'+name+"_dual.pdf"
        
        # # alg = heyting_from_poset(po)
        # # AlgebraIO.writeAlgebraFile(alg, alg_file_name)
        
        # # graph_dict = get_graph(alg)
        # # with open(graph_file_name,'w') as f:
            # # json.dump( graph_dict, f )
        # # os.system('python draw.py {}'.format(graph_file_name))
        
        
        # tex += "\\begin{center}\n$\\uparrow%s$:\n\n"%(upset)
        # tex += "\\begin{tabular}{cc}\n"
        # tex += "\\includegraphics[scale="+ str(scale) +"]{"+po_pdf_file_name+"} & "
        # tex += "\\includegraphics[scale="+ str(scale) +"]{"+alg_pdf_file_name+"} \\\\\n"
        # tex += "\\end{tabular}\n"
        # tex += "\\end{center}\n\n"
        
    
    # with open(tex_file_name,'w') as f:
        # f.write(tex)
    