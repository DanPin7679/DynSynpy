from pydantic import BaseModel, computed_field
from typing import Any, List, Dict, Optional
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import *

def pass_globals(module_globals):
    global main_global 
    main_global = module_globals 

class Param(BaseModel):
    name: str;
    description: str = "";
    symbol: Any= None

    def model_post_init(self, __context: Any) -> None: 
        self.symbol = sp.var(self.name)
        main_global[self.name] = self.symbol

class Flow(Param):
    eq: Any

    @computed_field
    @property
    def eq_symbol(self)->Any:
        return self.eq
        #return parse_expr(self.eq)

class Intermediary(Param):
    eq: Any

    @computed_field
    @property
    def eq_rhs_symbol(self) -> Any:
        return self.eq
        #return parse_expr(self.eq)

    @computed_field
    @property
    def _fn_symbol(self)-> Any:
        return sp.Function(self.name)(t)

    @computed_field
    @property
    def eq_symbol(self) -> Any:
        eq = sp.Eq(self._fn_symbol, self.eq_rhs_symbol)
        return eq

class Stock(Param):
    flow_in: Optional[Flow] = None;
    flow_out: Optional[Flow] = None;

    @computed_field
    @property
    def flow_net(self) -> Any:
        if self.flow_in == None: 
            if self.flow_out == None:
                raise Exception("Sorry, a stock need at least 1 flow") 
            else:
                return self.flow_out.eq_symbol
        else:
            if self.flow_out == None:
                return self.flow_in.eq_symbol
            else:
                return self.flow_in.eq_symbol - self.flow_out.eq_symbol

    @computed_field
    @property
    def _stock_symbol(self)-> Any:
        return sp.Function(self.name)(t)
    
    @computed_field
    @property
    def eq(self) -> Any:
        eq = sp.Eq(self._stock_symbol.diff(t), self.flow_net)
        return eq

            
class Module(Param):
    stocks: List[Stock]
    params: Optional[List[Param]] = []
    inters: Optional[List[Intermediary]] = []

    def model_post_init(self, __context) -> None:
        for s in self.stocks:
            self.__dict__[s.name] = s

class System(Param):
    modules: List[Module]

    def model_post_init(self, __context) -> None:
        for m in self.modules:
            self.__dict__[m.name] = m
    
    @computed_field
    @property
    def eqs(self) -> Any:
        eqs = []
        for m in self.modules:
            for s in m.stocks:
                eqs.append(s.eq)
        return eqs
    
    @computed_field
    @property
    def eqs_inter(self) -> Any:
        eqs = []
        for m in self.modules:
            for inter in m.inters:
                eqs.append(inter.eq_symbol)
        return eqs
    
        

    

    

