import sys
import os

base_letter = 'E'
dir_path = os.path.dirname(os.path.realpath(__file__))
dir = os.path.join(dir_path,'input')

os.chdir(dir_path)

sys.path.append("uacalc.jar")
import Queue
import re

from dmm import BasicAlgebra, AlgebraIO, AbstractOperation, add_arrow_and_meet, check_simple_chain, OperationSymbol, check_dmm
import itertools

# known operation constructions

b2xs3 = AlgebraIO.readAlgebraFile('input/b2xs3_reflection.ua')
        
class join_op(AbstractOperation):
    def intValueAt(self,args):
        join = b2xs3.getOperation(OperationSymbol("join",2))
        args = sorted(args)
        if args[0] < 7 and args[1] < 7:
            return join.intValueAt(args)
        elif args[0] <= 7 and args[1] == 7:
            return 7
        elif args[0] < 7:
            return join.intValueAt([args[0],args[1]-1])+1
        elif args[0] == 7:
            return args[1]
        else:
            return join.intValueAt([args[0]-1,args[1]-1])+1
            
        # return max(args)

def chain_join(cardinality):
    "Make join such that 0 is at the bottom and cardinality at the top."
    return join_op("join", 2, cardinality)

class neg_op(AbstractOperation):
    def intValueAt(self,args):
        return self.getSetSize()-1 - args[0]
        
def chain_neg(cardinality):
    "Make negation reversing the order of the elements."
    return neg_op("neg", 1, cardinality)

class e_op(AbstractOperation):
    def intValueAt(self,args):
        return 4
        
def chain_e(cardinality):
    "Make e operation."
    return e_op("e", 0, cardinality)

# since we know the algebra is rigorously compact we can specify certain elements
def chain_dot(unknowns,cardinality):
    "Make chain dot given the unknown values."
    class dot_op(AbstractOperation):
        def intValueAt(self, args):
        
            dot = b2xs3.getOperation(OperationSymbol("dot",2))
            
            e = chain_e(self.getSetSize()).intValueAt([])
            f = self.getSetSize()-1-e
            args = sorted(args) #a * b = b * a
            if 0 == args[0]: #0 * a = 0
                return 0
            # elif args[1] <= e : #a * b = a ^ b if a,b <= e
                # return args[0] #= min(args[0],args[1])
            # elif e == args[0]: #e * a = a
                # return args[1]
            # elif 1 == args[0] and f == args[1]: #f-1 = 1 * -1
                # return f
            # elif 1 == args[0] and f +1 == args[1]: #f-2 = 1 * f
                # return f
            # elif 3 == args[0] and 3 == args[1]: #f-1 = 1 * f-1
                # return 3
            # #elif 1 == args[0] and f-2 == args[1]: #f-2 = 1 * f-2
            # #    return f-2
            # #elif e+1 == args[0] and e+1 == args[1]: #e+1 = e+1 * e+1
            # #    return e+1
            # # elif f-2 == args[0] and f-2 == args[1]: #(f-2)^2 = T
                # # return self.getSetSize()-1
            # elif 3 <= args[0]: #a * b = T if a,b >= f-2
                # return self.getSetSize()-1
            elif args[0] != 7 and args[1] != 7:
                if args[0] < 7:
                    o1 = args[0]
                else:
                    o1 = args[0]-1
                if args[1] < 7:
                    o2 = args[1]
                else:
                    o2 = args[1]-1
                val = dot.intValueAt([o1,o2])
                if val < 7:
                    return val
                else:
                    return val + 1
            elif args[0] == 7 and args[1] == 7:
                return 7
            elif args[0] == 7 and args[1] >= 10:
                return self.getSetSize()-1
            elif self.getSetSize()-1 == args[1]: #T * a = T
                return self.getSetSize()-1
            else:
                return unknowns[args[0]][args[1]]
    
    return dot_op("dot", 2, cardinality)
    
known = []
uk = []
def already_known(cardinality,ind,ip,jp):
    if (ip,jp) in known or (ip,jp) in uk[:ind]:
        return True
    return False

def check_ass(values,cardinality,ind,a,b,c):
    # (a*b)*c
    m, x = min(a,b), max(a,b)
    if already_known(cardinality,ind,x,m):
        a_b = values[m][x]
        m, x = min(a_b,c), max(a_b,c)
        if already_known(cardinality,ind,x,m):
            return values[m][x]
            
def add_to_fixed(fixed_set,value):
    fixed_set.add(value)
    if len(fixed_set) > 1:
        raise StopIteration
            

def make_dots(cardinality, ind=0, values=None):
    "recursively make dots"
    e = chain_e(cardinality).intValueAt([])
    f = cardinality-1-e
    
    # If this is called from outside
    if values == None:
        values = {}
        blank_dot = chain_dot({},cardinality)
        for x in range(cardinality):
            values[x] = {}
            for y in range(x,cardinality):
                try:
                    values[x][y] = blank_dot.intValueAt([x,y])
                    known.append((x,y))
                except KeyError:
                    uk.append((x,y))
                    pass
        
    j,i = uk[ind]
            
    ## use associativity to fix some values
    
    # loop through known values to see if 
    fixed_set = set([])
    
    for jp,ip in known+uk[:ind]:
        if values[jp][ip] == j: #jp*ip = j
            # jp*(ip*i)
            add_to_fixed( fixed_set, check_ass(values,cardinality,ind,jp,ip,i) )
            # ip*(jp*i)
            add_to_fixed( fixed_set, check_ass(values,cardinality,ind,ip,jp,i) )
            
        if values[jp][ip] == i: #jp*ip = i
            # (j*jp)*ip
            add_to_fixed( fixed_set, check_ass(values,cardinality,ind,j,jp,ip) )
            # (j*ip)*jp
            add_to_fixed( fixed_set, check_ass(values,cardinality,ind,j,ip,jp) )
            
    fixed = None
    if len(fixed_set) > 0:
        fixed = fixed_set.pop()
    
    if fixed != None: # Associativity has fixed the value
        lower = fixed
        upper = fixed
    else:   # Associativity gave us no information, so we set upper and lower bounds using other conditions
                
        # set lower bound
        lower = j # order compatability since i is greater than e
        
        if i != j: 
            lower = max(lower,values[j][i-1]) # order compatability, first
            lower = max(lower,values[j-1][i]) # order compatability, second
        else: # diagonal
            lower = max(lower,i) # square increasing
            # if i > 2: 
                # lower = max(lower,values[i-1][i-1]) # increasing sequence
        if i > cardinality - j - 1: # i > neg j => i.j > f
            lower = max(lower,f+1)
        
        
        # set upper bound
        upper = cardinality-1
        if i == cardinality - j - 1: # i = neg j => i.j <= f
            upper = min(upper,f)
       
    # print lower,upper
    # check every possible value between lower and upper
    for k in range(lower,upper+1):
        values[j][i]=k
        if ind==len(uk)-1:
            yield values
        else:
            for val in make_dots(cardinality, ind+1, values):
                yield val
            

def build_and_check_alg(cardinality,values):
    # if not (
            # (values[1][cardinality-1-1] > 3 and values[1][cardinality-1-1] < cardinality-1-3) or
            # (values[1][cardinality-1-2] > 3 and values[1][cardinality-1-2] < cardinality-1-3) or
            # (values[2][cardinality-1-2] > 3 and values[2][cardinality-1-2] < cardinality-1-3) or
            # (values[2][cardinality-1-1] > 3 and values[2][cardinality-1-1] < cardinality-1-3)
        # ):
        # return False
    # print values
    join = chain_join(cardinality)
    neg = chain_neg(cardinality)
    e = chain_e(cardinality)
    
    dot = chain_dot(values,cardinality)
    ops = join,neg,e,dot
    
    value_list = (str(values[x][y]) for x in values for y in values[x])
    number = "".join(value_list)
    alg = BasicAlgebra("%s_{%d}^{%s}"%(base_letter,cardinality,number), cardinality, ops)
    alg = add_arrow_and_meet(alg)
    if check_dmm(alg,example=False):
    # if not check_simple_chain(alg):
        print "found example "+number
        # write file
        alg_file_name = os.path.join(dir,"%s-%d-%s.ua"%(base_letter,cardinality,number))
        AlgebraIO.writeAlgebraFile(alg, alg_file_name)
        return True
    else:
        return False
    

if __name__=="__main__":
    import re
    cardinality = 15
    thread_num = 0
    help_text = """
    Usage: find_simple_chains [options]
    
    Options:
    -pn: number of threads (default n=%d)
    -h: show this help txt
    """%(thread_num)
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
            
    # start benchmark
    from datetime import datetime
    now = datetime.now()
    
    # find simple chains and save them
    if thread_num == 0:
        print "Finding chains"
        count = 0
        for values in make_dots(cardinality):
            # st = ""
            # for x,y in uk:
                # st = st+str(values[x][y])
            # print st
            count = count+1
        print count, "iterations"
            
        map(lambda x: build_and_check_alg(cardinality,x), make_dots(cardinality))
    else:
        
        import threading
        from copy import deepcopy
        if thread_num > 3:
            print "It seems that 3 threads are the maximum safe number, so using that instead."
            thread_num = 3
        print "Finding chains"
        
        threads = [None]*thread_num
        
        for value in make_dots(cardinality):
            value_copy = deepcopy(value)
            wait = True
            for i,thread in enumerate(threads):
                if thread == None or not thread.is_alive():
                    threads[i] = threading.Thread(target=lambda: build_and_check_alg(cardinality,value_copy))
                    threads[i].start()
                    wait = False
                    break
            if wait:
                threads[0].join() # we just wait for the first thread to finish (not very clever)
        # make sure all threads are done
        for thread in threads:
            thread.join()
            
    print "took", (datetime.now()-now).seconds/60., "mins"
                    
    # rename them into something more reasonable
    import glob
    paths = sorted(glob.glob(dir+r'/'+base_letter+'-'+str(cardinality)+r'-*.ua'),  key=os.path.getmtime)

    old_algs = []
    for path in paths:
        alg = AlgebraIO.readAlgebraFile(path)
        old_algs.append([alg,path])
        
    number = 1
    new_algs = []
    for alg,path in old_algs:
        alg.setName("%s-{%d}-{%d}"%(base_letter,cardinality,number))
        alg_file_name = os.path.join(dir,"%s-%d-%d.ua"%(base_letter,cardinality,number))
        new_algs.append([alg,alg_file_name])
        number = number + 1
        print alg.getName(), "deleting", path
        os.remove(path)
        
    for alg,path in new_algs:
        print "writing", alg.getName(), "to", path
        AlgebraIO.writeAlgebraFile(alg, path)
