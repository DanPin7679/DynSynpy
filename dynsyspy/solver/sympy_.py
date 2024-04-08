import sympy as sp
from sympy.abc import *

def discrete(t_span, results, eqs, _):
        i=0
        for ts in t_span:
            j=0
            for eq in eqs:
                res=list(sp.solve(eq.subs(t,ts))[0].values())[0]
                results.iloc[i,j] = float(res)
                j+=1
            i+=1   
        return results