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

    def model_post_init(self, __context: Any) -> None: 
        main_global[self.name] = sp.var(self.name)

    @computed_field
    @property
    def var_sym(self)->Any:
        return sp.Symbol(self.name)
    
    @computed_field
    @property
    def fn_sym(self)->Any:
        return sp.Function(self.name)
    
    @computed_field
    @property
    def fn_sym_of_t(self)->Any:
        return self.fn_sym(t)
    
    def latex(self) -> str:
        return sp.latex(self.var_sym)

    def print(self) -> str:
        for i in self.latex():
            display(Math(i))

class Param(Item):
    _: Any = None

class Flow(Item):
    eq: Any

    def latex_eq(self) -> str:
        return sp.latex(self.eq)

    def print_eq(self) -> str:
        for i in self.latex():
            display(Math(i))

class Intermediary(Item):
    eq_rhs: Any

    @computed_field
    @property
    def eq(self) -> Any:
        eq = sp.Eq(self.fn_sym_of_t, self.eq_rhs)
        return eq
    
    def latex(self) -> str:
        return sp.latex(self.eq)

    def print(self) -> str:
        display(Math(self.latex))

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
                return self.flow_out.eq
        else:
            if self.flow_out == None:
                return self.flow_in.eq
            else:
                return self.flow_in.eq - self.flow_out.eq
    
    @computed_field
    @property
    def eq(self) -> Any:
        eq = sp.Eq(self.fn_sym_of_t.diff(t), self.flow_net)
        return eq
    
    def latex_eq(self) -> str:
        res = [
            sp.latex(self.eq)
        ]
        res.append("")
        return res
        
    def print(self) -> str:
        for i in self.latex_eq():
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
            latex_list=latex_list+s.latex_eq()

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
    def _all_items(self)->Any:
        all_items = {
            "param": [],
            "stock": [],
            "flow": [],
            "inter": []
        }
        for m in self.modules:
            for p in m.params:
                all_items["param"].append(p)
            for s in m.stocks:
                all_items["stock"].append(s)
                if s.flow_in!=None: all_items["flow"].append(s.flow_in)
                if s.flow_out!=None: all_items["flow"].append(s.flow_out) 
            for inter in m.inters:
                all_items["inter"].append(inter)
        return all_items
    
    @computed_field
    @property
    def eqs_stock(self) -> Any:
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
                eqs.append(inter.eq)
        return eqs
    
    def latex(self) -> str:
        latex_list = [f"{sp.latex(self.name)}"]
        for m in self.modules:
            latex_list=latex_list+m.latex()
        
        return latex_list
    
    def print(self) -> str:
        for i in self.latex():
            display(Math(i))
    
        

    

    

