import pytest
from dynsyspy.system import Param, Flow, Stock, Module,System
import sympy as sp
from sympy.abc import *

sp.var("b_r d_r a_r")
br = Param(name="b_r", description="Birth Rate")
dr = Param(name="d_r", description="")
flow_in = Flow(name="birth", eq="b_r * P")
flow_out = Flow(name="death", eq="d_r * P")
Ps = Stock(name="P", flow_in=flow_in, flow_out=flow_out)

ar = Param(name="a_r", description="Tech Growth Rate")
flow_in_a = Flow(name="tech_incr", eq="a_r * A")
As = Stock(name="A", flow_in=flow_in_a)

mod = Module(name="Econ", stocks=[Ps, As], params=[br, dr, ar])
sys = System(name="Solow", modules=[mod])

def test_param():
    test_param = br
    assert test_param.symbol == sp.Symbol("b_r")

def test_param_symbol():
    test_param = br
    assert test_param.name == "b_r"

def test_param_no_descp():
    test_param = dr
    assert test_param.description == ""

def test_flow_eq_symbol():
    eq = b_r * P
    testFlow = flow_in
    assert testFlow.eq_symbol == eq

def test_stock_no_flow():
    with pytest.raises(Exception) as e_info:
            s=Stock(name="P")
            s.flow_net

def test_stock_eq_flownet():
    f_in = b_r * P
    f_out = d_r * P
    f_net = f_in - f_out
    
    assert Ps.flow_net == f_net

def test_module_stock_attr():
     assert mod.A.name == "A"

def test_syst():
     assert sys.name == "Solow"

def test_syst_mod_attr():
     assert sys.Econ.P.name == "P"
