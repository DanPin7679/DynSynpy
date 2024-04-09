import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
from pydantic import BaseModel, computed_field
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import *
from dynsyspy.system import System, Item
from dynsyspy.solver import custom, sympy_
from dynsyspy.types.problem import ProblemType, Solver



class Problem(BaseModel):
    name: str;
    description: str = "";
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
        for m in self.system.modules:
            for s in m.stocks:
                data[s.name] = np.zeros(len(self.t_span), dtype=np.float64)
        df=pd.DataFrame(data=data)
        df.insert(0, "Time", self.t_span, True)
        return df
    
    def solve(self)->Any:
        stocks_sym = [s.var_sym for s in self.system._all_items["stock"]]
        params_sym = [p.var_sym for p in self.system._all_items["param"]]
        results = self._results()
        eqs=[]
        eqs_sympy=[]
        init_vals_sympy = dict()

        for eq in self.system.eqs_stock:
            for inter_sym in self.system._all_items["inter"]:
                eq = eq.subs(inter_sym.var_sym, inter_sym.eq_rhs)
            eqs.append(eq)
    
        match (self.solver):
            case (Solver.sympy):
                eqs_init_val = sp.dsolve(eqs_sympy, ics=init_vals_sympy)
                self.results = sympy_.discrete(self.t_span, results, eqs_init_val, self.problem_type)
            case (Solver.custom):
                init_vals = np.array([self.init_vals[sym] for sym in stocks_sym])
                params_vals = np.array([self.param_vals[sym] for sym in params_sym])
                lambdas = np.array([sp.lambdify((t, (stocks_sym, params_sym)), eq.rhs) for eq in eqs])
                self.results = custom.solve(results, lambdas, init_vals, params_vals, self.problem_type)
            case _:
                print('This solver does not exist')

        res_stocks = [results[s.name] for s in stocks_sym]
        res_params = [self.param_vals[s] for s in params_sym]
        
        for m in self.system.modules:
            for inter in m.inters:
                eq_symbol = inter.eq_rhs
                eq_lambda = sp.lambdify((stocks_sym, params_sym), eq_symbol)
                eq = eq_lambda(res_stocks, res_params)
                self.results[inter.name] = eq
            for s in m.stocks:
                if s.flow_in != None:
                    eq_symbol = s.flow_in.eq
                    for inter_sym in self.system._all_items["inter"]:
                        eq_symbol = eq_symbol.subs(inter_sym.var_sym, inter_sym.eq_rhs)
                    eq_lambda = sp.lambdify((stocks_sym, params_sym), eq_symbol)
                    eq = eq_lambda(res_stocks, res_params)
                    self.results[s.flow_in.name] = eq
                if s.flow_out != None:
                    eq_symbol = s.flow_out.eq
                    for inter_sym in self.system._all_items["inter"]:
                        eq_symbol = eq_symbol.subs(inter_sym.var_sym, inter_sym.eq_rhs)
                    eq_lambda = sp.lambdify((stocks_sym, params_sym), eq_symbol)
                    eq = eq_lambda(res_stocks, res_params)
                    self.results[s.flow_out.name] = eq


        



      

