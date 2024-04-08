import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import *
from dynsyspy.system import System, Param
from dynsyspy.solver import custom, sympy_
from dynsyspy.types.problem import ProblemType, Solver



class Problem(Param):
    system: System;
    t_span: Any;
    init_vals: Optional[Dict] = {};
    param_vals: Optional[Dict] = {};
    policy_vals: Optional[Dict] = {};
    problem_type: ProblemType = ProblemType.discrete
    solver: Solver = Solver.custom
    results: Any = None

    def _results(self)->Any:
        data=dict()
        self._stock_syms = []
        self._stock_syms_fn = []
        self._inter_syms_subs = []
        for m in self.system.modules:
            for s in m.stocks:
                data[s.name] = np.zeros(len(self.t_span), dtype=np.float64)
                self._stock_syms.append(s.symbol)
                self._stock_syms_fn.append((s.symbol, s._stock_symbol))
            for inter in m.inters:
                self._inter_syms_subs.append((inter.symbol, inter.eq_rhs_symbol))

        df=pd.DataFrame(data=data)
        df.insert(0, "Time", self.t_span, True)
        return df
    
    def solve(self)->Any:
        results = self._results()
        eqs=[]
        eqs_sympy=[]
        init_vals_sympy = dict()

        for eq in self.system.eqs:
            for inter_sym in self._inter_syms_subs:
                eq = eq.subs(inter_sym[0], inter_sym[1])
            eq = eq.subs(self.param_vals)
            eqs.append(eq)

            """for sym in self._stock_syms_fn:
                eq_params = eq_params.subs(sym[0], sym[1])
                init_vals_sympy[sym[1].subs(t, 0)] = self.init_vals[sym[0]]
            eqs_sympy.append(eq_params)"""
    
        match (self.solver):
            case (Solver.sympy):
                eqs_init_val = sp.dsolve(eqs_sympy, ics=init_vals_sympy)
                self.results = sympy_.discrete(self.t_span, results, eqs_init_val, self.problem_type)
                return self.results
            case (Solver.custom):
                init_vals = np.array([self.init_vals[sym] for sym in self._stock_syms])
                lambdas = np.array([sp.lambdify((t, self._stock_syms), eq.rhs) for eq in eqs])
                self.results =custom.solve(results, lambdas, init_vals, self.problem_type)
                return self.results
            case _:
                print('This solver does not exist')

        



      
