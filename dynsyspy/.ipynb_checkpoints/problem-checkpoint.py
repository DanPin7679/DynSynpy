import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import *
from dynsyspy.system import System, Param
from enum import Enum
from dynsyspy.solver import custom, sympy_


class ProblemType(str, Enum):
    discrete = 'discrete'

class Solver(str, Enum):
    custom = 'custom'  
    sympy = 'sympy'

class Problem(Param):
    system: System;
    t_span: Any;
    init_vals: Optional[Dict] = {};
    param_vals: Optional[Dict] = {};
    policy_vals: Optional[Dict] = {};
    problem_type: ProblemType = ProblemType.discrete
    solver: Solver = Solver.custom

    def _results(self)->Any:
        data=dict()
        for m in self.system.modules:
            for s in m.stocks:
                data[s.name] = np.zeros(len(self.t_span))
        return pd.DataFrame(data=data, index=self.t_span)
    
    def solve(self)->Any:
        results = self._results()
        eqs=[]
        for eq in self.system.eqs:
            eq_params = eq.subs(self.param_vals)
            eqs.append(eq_params)
            
        eqs_init_val = sp.dsolve(eqs, ics=self.init_vals)
    
        match (self.solver):
            case (Solver.sympy):
                return sympy_.discrete(self.t_span, results, eqs_init_val, self.problem_type)
        match (self.solver):
            case (Solver.custom):
                lambdas = [sp.lambdify(t, eq.rhs) for eq in eqs_init_val]

                return custom.discrete(self.t_span, results, lambdas, self.problem_type)
            case _:
                print('This mix does not work')

        



      

