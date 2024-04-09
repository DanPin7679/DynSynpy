import numpy as np
import pandas as pd
from functools import cached_property
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

    @computed_field
    @cached_property
    def _params(self)->Any:
        params = self.system._all_items["param"]
        syms = [p.var_sym for p in params if isinstance(self.param_vals[p.var_sym], (int, float))]
        vals = [self.param_vals[p.var_sym]   for p in params if isinstance(self.param_vals[p.var_sym], (int, float))]
        print(syms, vals)
        return syms, vals
    
    @computed_field
    @cached_property
    def _params_array(self)->Any:
        params = self.system._all_items["param"]
        syms = [p.var_sym for p in params if isinstance(self.param_vals[p.var_sym], (list, np.ndarray, pd.Series))]
        vals = [self.param_vals[p.var_sym]   for p in params if isinstance(self.param_vals[p.var_sym], (list, np.ndarray, pd.Series))]
        return syms, vals

    def _results(self)->Any:
        data=dict()
        for m in self.system.modules:
            for s in m.stocks:
                data[s.name] = np.zeros(len(self.t_span), dtype=np.float64)
        df=pd.DataFrame(data=data)
        df.insert(0, "Time", self.t_span, True)
        return df
    
    def _subs_inter(self, eqs_in):
        eqs=[]
        for eq in eqs_in:
            for inter_sym in self.system._all_items["inter"]:
                eq = eq.subs(inter_sym.var_sym, inter_sym.eq_rhs)
            eqs.append(eq)
        return eqs
    
    def _subs_param_array(self, eqs_in):
        syms, vals = self._params_array
        
        eqs=[]
        for eq in eqs_in:
            i=0
            for sym in syms:
                l = [0.25 for _ in self.t_span]
                arr = sp.Array(vals[i])[t]
                eq = eq.subs(sym, arr)
                i+=1
            eqs.append(eq)
        return eqs

    def _create_inter_results(self, stocks_sym, params_sym):
        res_stocks = [self.results[s.name] for s in stocks_sym]
        res_params = [self.param_vals[s] for s in params_sym]
        
        for inter in self.system._all_items["inter"]:
            eq = sp.lambdify((stocks_sym, params_sym), inter.eq_rhs)(res_stocks, res_params)
            self.results[inter.name] = eq
        for flow in self.system._all_items["flow"]:
            for inter_sym in self.system._all_items["inter"]:
                eq_symbol = flow.eq.subs(inter_sym.var_sym, inter_sym.eq_rhs)
            eq = sp.lambdify((stocks_sym, params_sym), eq_symbol)(res_stocks, res_params)
            self.results[flow.name] = eq
            
    def solve(self)->Any:
        stocks_sym = [s.var_sym for s in self.system._all_items["stock"]]
        results = self._results()
        eqs = self._subs_inter(self.system.eqs_stock)
        eqs = self._subs_param_array(eqs)

        match (self.solver):
            case (Solver.custom):
                self.results = self._solver_custom(eqs, results, stocks_sym, self._params[0])
            case _:
                print('This solver does not exist')

        self._create_inter_results(stocks_sym, self._params[0])

    def _solver_custom(self, eqs, results, stocks_sym, params_sym)->Any:
        init_vals = np.array([self.init_vals[sym] for sym in stocks_sym])
        lambdas = np.array([sp.lambdify((t, (stocks_sym, params_sym)), eq.rhs) for eq in eqs])
        return custom.solve(results, lambdas, init_vals, self._params[1], self.problem_type)
        


        



      

