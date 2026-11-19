import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')
out_file_name = os.path.join(dir_path,'output/ManyPowers5.tex')

os.chdir(dir_path)

sys.path.append("uacalc.jar")
sys.path.append("LatDraw.jar")

from org.uacalc.alg.sublat import SubalgebraLattice
import glob

from dmm import AlgebraIO, OperationSymbol,check_dmm
from latex import get_operation_table

paths = sorted(glob.glob(dir+r'/simple_chains_power5_*-*.ua'),  key=os.path.getmtime)


the_string = """
\\documentclass[11pt]{amsart}

\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{amsthm}
\\usepackage{graphicx}


\\title{A lot of covers of $\\mathbb{V}(\\mathbf{C_4})$}

\\begin{document}

\\maketitle

\\allowdisplaybreaks

"""
algebras = []
for path in paths:
    alg = AlgebraIO.readAlgebraFile(path)
    # # sanity check
    # if not check_dmm(alg):
        # raise Exception(alg.getName()+" is not a De Morgan Monoid!!!\n")
    algebras.append(alg)
algebras = sorted(algebras, key=lambda alg: alg.cardinality())


for alg in algebras:
    subalg = SubalgebraLattice(alg)
    if subalg.cardinality() <= 2:
        print alg.getName(), subalg.cardinality()
        # print algebras name
        the_string += "\\begin{center}\n$\\mathbf{%s}$:\n\n\\nopagebreak[4]\n\\vspace{0.6em}\n"%( alg.getName() )
        dot = alg.getOperation(OperationSymbol("dot",2))
        neg = alg.getOperation(OperationSymbol("neg",1))
        a_op = alg.getOperation(OperationSymbol("a",0))
        a = a_op.intValueAt([])
        # get labels of powers and negation
        labels = [""]*alg.cardinality()
        labels[0] = '0'
        labels[1] = 'e'
        labels[a] = 'a'
        i = 2
        power = dot.intValueAt([a,a])
        powers = [a,dot.intValueAt([a,a])]
        
        # add powers of a until an idempotent element is reached
        while True:
            if len(labels[power]) > 0:
                labels[power] = 'a^{%s} = %s'%(i, labels[power])
                break
            labels[power] = 'a^{%d}'%(i)
            i = i+1
            power = dot.intValueAt([a,power])
            powers.append(power)
            
        # add negations of powers
        neg_labels = [""]*alg.cardinality()
        for i,power in enumerate(powers):
            if power < alg.cardinality()-1:
                neg_power = alg.cardinality()-1-power
                if len(neg_labels[neg_power]) == 0:
                    neg_labels[neg_power] = '\\neg(a^{%d})'%(i+1)
        
        # combine
        for i,label in enumerate(labels):
            if len(label)>0 and len(neg_labels[i])>0:
                labels[i] = neg_labels[i] + ' = ' + label
            elif len(neg_labels[i])>0:
                labels[i] = neg_labels[i]
        
        # the_string += "\\begin{center}\n\n"
        the_string += get_operation_table(dot,labels) + '\\vspace{0.6em}\n'
        the_string += "\\end{center}\n\n"
        

the_string += """
\\end{document}
"""

with open(out_file_name,'w') as f:
    f.write(the_string)
