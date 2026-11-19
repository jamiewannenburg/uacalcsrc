import itertools
args = [x for x in itertools.product(range(2),range(2))]
ans = [# (0,0),(0,1),(1,0),(1,1)
        [(0,0),(0,0),(0,0),(0,0)],#(0, 0)
        [(0,0),(0,1),(1,0),(1,1)],#(0, 1)
        [(0,0),(1,0),(1,1),(1,1)],#(1, 0)
        [(0,0),(1,1),(1,1),(1,1)] #(1, 1)
]
def to(x,y):
    return int((not x)|y)
def fun(a,b):
    return (
        int((a[1]|a[0])&(b[0]|b[1])&(a[0]|b[0])),
        int((a[1]&b[1])|(a[0]&b[0]))
    )
print('  *  ',args)
for a in args:
    print(a,end='|')
    for b in args:
        print("({}, {}),".format(*fun(a,b)),end=' ')
    print()
print()
print('  *  ',args)
for i,a in enumerate(args):
    print(a,end='|')
    for j,b in enumerate(args):
        print("{}".format(fun(a,b)==ans[i][j]),end=' ')
    print()
print()
print('  *  ',args)
for i,a in enumerate(args):
    print(a,end='|')
    for j,b in enumerate(args):
        print("{}".format(fun(a,b)[0]==ans[i][j][0]),end=' ')
    print()
print()
print('  *  ',args)
for i,a in enumerate(args):
    print(a,end='|')
    for j,b in enumerate(args):
        print("{}".format(fun(a,b)[1]==ans[i][j][1]),end=' ')
    print()
#a[b[0]]&b[a[0]],a[b[1]]&b[a[1]]