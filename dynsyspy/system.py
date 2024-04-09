from IPython.display import display, Math, Markdown, Latex
from pydantic import BaseModel, computed_field
from typing import Any, List, Dict, Optional
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import *

def pass_globals(module_globals):
    global main_global 
    main_global = module_globals 

class Item(BaseModel):
    name: str;
    description: str = "";
    symbol: Any = None
    isFunction:bool = False

    def model_post_init(self, __context: Any) -> None: 
        self.symbol = sp.var(self.name)
        main_global[self.name] = self.symbol

class Param(Item):
    name: str;
    description: str = "";
    symbol: Any = None
    isFunction:bool = False

    def model_post_init(self, __context: Any) -> None: 
        """if self.isFunction:
            print(self.name)
            self.symbol = sp.var(self.name, cls=sp.Function)
            main_global[self.name] = self.symbol
        else:"""
        self.symbol = sp.var(self.name)
        main_global[self.name] = self.symbol

    def latex(self) -> str:
        return sp.latex(self.symbol)

    def print(self) -> str:
        for i in self.latex():
            display(Math(i))

class Flow(Item):
    eq: Any

    @computed_field
    @property
    def eq_symbol(self)->Any:
        return self.eq

    def latex(self) -> str:
        return sp.latex(self.eq_symbol)

    def print(self) -> str:
        for i in self.latex():
            display(Math(i))

class Intermediary(Item):
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
    
    def latex(self) -> str:
        return sp.latex(self.eq_symbol)

    def print(self) -> str:
        for i in self.latex():
            display(Math(i))

class Stock(Item):
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
    
    def latex(self) -> str:
        res = [
            sp.latex(self.eq)
        ]

        """
        f"{sp.latex('where')}"
        if self.flow_in != None:
            res.append( self.flow_in.latex(),)
        if self.flow_out != None:
                res.append( self.flow_out.latex(),)"""
        res.append("")
        return res
        
    def print(self) -> str:
        for i in self.latex():
            display(Math(i))

            
class Module(Item):
    stocks: List[Stock]
    params: Optional[List[Param]] = []
    inters: Optional[List[Intermediary]] = []

    def model_post_init(self, __context) -> None:
        for s in self.stocks:
            self.__dict__[s.name] = s

    def latex(self) -> str:
        latex_list = [f"{sp.latex(self.name)}"]
        for s in self.stocks:
            latex_list=latex_list+s.latex()

        latex_list.append(f"where")
        for p in self.params:
            latex_list.append(p.latex() + f": {p.description}")

        return latex_list
    

    def print(self) -> str:
        for i in self.latex():
            display(Math(i))

class System(Item):
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
    
    def latex(self) -> str:
        latex_list = [f"{sp.latex(self.name)}"]
        for m in self.modules:
            latex_list=latex_list+m.latex()
        
        return latex_list
    
    def print(self) -> str:
        for i in self.latex():
            display(Math(i))
    
        

    

    

