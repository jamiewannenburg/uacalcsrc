import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')

os.chdir(dir_path)

sys.path.append("uacalc.jar")
import Queue
import re

from dmm import BasicAlgebra, AlgebraIO, AbstractOperation, add_arrow_and_meet, check_simple_chain, OperationSymbol
import itertools

# known operation constructions

class join_op(AbstractOperation):
    def intValueAt(self,args):
        return max(args)

def chain_join(cardinality):
    "Make join such that 0 is at the bottom and cardinality at the top."
    return join_op("join", 2, cardinality)

class neg_op(AbstractOperation):
    def intValueAt(self,args):
        return self.getSetSize()-1 - args[0]
        
def chain_neg(cardinality):
    "Make negation reversing the order of the elements."
    return neg_op("neg", 1, cardinality)

# in this case we know that e will be the above the bottom, since the algebra is simple
class e_op(AbstractOperation):
    def intValueAt(self,args):
        return 1
        
def chain_e(cardinality):
    "Make e operation."
    return e_op("e", 0, cardinality)

# since we know the algebra is rigorously compact we can specify certain elements
def chain_dot(unknowns,cardinality):
    "Make chain dot given the unknown values."
    class dot_op(AbstractOperation):
        def intValueAt(self, args):
            args = sorted(args)
            if 0 == args[0]:
                return 0
            elif 1 == args[0]:
                return args[1]
            elif self.getSetSize()-1 == args[1]:
                return self.getSetSize()-1
            else:
                return unknowns[args[0]][args[1]]
    
    return dot_op("dot", 2, cardinality)
    
def already_known(cardinality,i,j,ip,jp):
    if jp < j and ip < cardinality-1:
        return True
    elif jp==j:
        return ip < i
    return False

def make_dots(cardinality, i=2, j=2, values=None):
    "recursively make dots"
    
    # If this is called from outside
    if values == None:
        values = {}
        for x in range(2,cardinality-1):
            values[x] = {}
            
    
    # the last pair
    if i == cardinality-2 and j == cardinality-2:
        values[j][i]=cardinality-1 # we know f.f = top
        yield values
        
    else:
        
        ## use associativity to fix some values
        
        # loop through known values to see if 
        fixed = None
        
        for jp in range(2,j+1):
            i_max = cardinality -2
            if j==jp:
                i_max = i-1
            for ip in range(jp,i_max+1):
                
                if values[jp][ip] == i: #jp*ip = i
                    # (j*jp)*ip
                    m = min(j,jp)
                    x = max(j,jp)
                    if already_known(cardinality,i,j,x,m):
                        a = values[m][x]
                        m = min(a,ip)
                        x = max(a,ip)
                        if already_known(cardinality,i,j,x,m):
                            fixed1 = values[m][x]
                            if fixed == None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    raise StopIteration
                        
                    # (j*ip)*jp
                    m = min(j,ip)
                    x = max(j,ip)
                    if already_known(cardinality,i,j,x,m):
                        a = values[m][x]
                        m = min(a,jp)
                        x = max(a,jp)
                        if already_known(cardinality,i,j,x,m):
                            fixed1 = values[m][x]
                            if fixed == None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    raise StopIteration
                        
                if values[jp][ip] == j:  #jp*ip = j
                    # jp*(ip*i)
                    m = min(i,ip)
                    x = max(i,ip)
                    if already_known(cardinality,i,j,x,m):
                        a = values[m][x]
                        m = min(a,jp)
                        x = max(a,jp)
                        if already_known(cardinality,i,j,x,m):
                            fixed1 = values[m][x]
                            if fixed == None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    raise StopIteration
                        
                    # ip*(jp*i)
                    m = min(i,jp)
                    x = max(i,jp)
                    if already_known(cardinality,i,j,x,m):
                        a = values[m][x]
                        m = min(a,ip)
                        x = max(a,ip)
                        if already_known(cardinality,i,j,x,m):
                            fixed1 = values[m][x]
                            if fixed == None:
                                fixed = fixed1
                            else:
                                if fixed != fixed1:
                                    raise StopIteration
                    
                        
        if fixed != None: # Associativity has fixed the value
            lower = fixed
            upper = fixed
        else:   # Associativity gave us no information, so we set upper and lower bounds using other conditions
                    
            # set lower bound
            lower = max(i,j) # order compatability since i and j are greater than e
            
            if i>2 and i > j: # order compatability, first
                lower = max(lower,values[j][i-1])
            if j>2 and i > j: # order compatability, second
                lower = max(lower,values[j-1][i])
            if i==j: # diagonal
                if cardinality <= 6:
                    lower = max(lower,i) # square increasing
                else:
                    lower = max(lower,i+1) # strictly square increasing (for cardinalities greater than 6)
                if i > 2: 
                    lower = max(lower,values[i-1][i-1]) # increasing sequence
            if i > cardinality - j - 1: # i > neg j => i.j > f
                lower = max(lower,cardinality -1)
            
            
            # set upper bound
            upper = cardinality-1
            if i == cardinality - j - 1: # i = neg j => i.j <= f
               upper = min(upper,cardinality -2)
           
        # get next i and j
        new_i = i+1
        new_j = j
        if i == cardinality-2:
            new_i = j+1
            new_j = j+1
        
        
        # check every possible value between lower and upper
        for k in range(lower,upper+1):
            values[j][i]=k
            
            for val in make_dots(cardinality, new_i, new_j, values):
                yield val
            

def build_and_check_alg(cardinality,values):
    
    join = chain_join(cardinality)
    neg = chain_neg(cardinality)
    e = chain_e(cardinality)
    
    dot = chain_dot(values,cardinality)
    ops = join,neg,e,dot
    
    value_list = (str(values[x][y]) for x in values for y in values[x])
    number = "".join(value_list)
    alg = BasicAlgebra("C_{%d}^{%s}"%(cardinality,number), cardinality, ops)
    alg = add_arrow_and_meet(alg)
    if not check_simple_chain(alg):
        print "found example "+number
        # write file
        alg_file_name = os.path.join(dir,"C-%d-%s.ua"%(cardinality,number))
        AlgebraIO.writeAlgebraFile(alg, alg_file_name)
        return True
    else:
        return False
    

if __name__=="__main__":
    import re
    min_cardinality = 5
    max_cardinality = 8 #greater than min_cardinality
    thread_num = 0
    help_text = """
    Usage: find_simple_chains [options] [min cardinality [max cardinality]]
    If no cardinality is supplied the min = %d and max = %d.
    If one cardinality is supplied then both min and max is the supplied one.
    
    Options:
    -pn: number of threads (default n=%d)
    -h: show this help txt
    """%(min_cardinality,max_cardinality,thread_num)
    argv_noopt = []
    for arg in sys.argv:
        m = re.search(r'-p(\d+)',arg)
        if m:
            thread_num = int(m.group(1))
        elif arg == "-h":
            print help_text
            exit()
        else:
            argv_noopt.append(arg)
            
    
    if len(argv_noopt) > 1:
        min_cardinality = int(argv_noopt[1])
        max_cardinality = min_cardinality
    if len(argv_noopt) > 2:
        max_cardinality = int(argv_noopt[2])
        
    # find simple chains and save them
    if thread_num == 0:
        for n in range(min_cardinality,max_cardinality+1):
            print "Finding simple chains with cardinality "+str(n)
            map(lambda x: build_and_check_alg(n,x), make_dots(n))
    else:
        
        import threading
        from copy import deepcopy
            
        for n in range(min_cardinality,max_cardinality+1):
            print "Finding simple chains with cardinality "+str(n)
            
            threads = [None]*thread_num
            
            for value in make_dots(n):
                value_copy = deepcopy(value)
                wait = True
                for i,thread in enumerate(threads):
                    if thread == None or not thread.is_alive():
                        threads[i] = threading.Thread(target=lambda: build_and_check_alg(n,value_copy))
                        threads[i].start()
                        wait = False
                        break
                if wait:
                    threads[0].join() # we just wait for the first thread to finish (not very clever)
            # make sure all threads are done
            for thread in threads:
                thread.join()
                    
    # rename them into something more reasonable
    import glob
    for n in range(min_cardinality,max_cardinality+1):
        paths = sorted(glob.glob(dir+r'/C-'+str(n)+r'-*.ua'),  key=os.path.getmtime)

        old_algs = []
        for path in paths:
            alg = AlgebraIO.readAlgebraFile(path)
            old_algs.append([alg,path])
            
        number = 1
        new_algs = []
        for alg,path in old_algs:
            alg.setName("C-{%d}-{%d}"%(n,number))
            alg_file_name = os.path.join(dir,"C-%d-%d.ua"%(n,number))
            new_algs.append([alg,alg_file_name])
            number = number + 1
            print alg.getName(), "deleting", path
            os.remove(path)
            
        for alg,path in new_algs:
            print "writing", alg.getName(), "to", path
            AlgebraIO.writeAlgebraFile(alg, path)
