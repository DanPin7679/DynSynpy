import pytest
import numpy as np
from dynsyspy.system import Param, Flow, Stock, Module,System
from dynsyspy.problem import Problem
import sympy as sp
from sympy.abc import *

fP = sp.Function('P')
fA = sp.Function('A')
sp.var("b_r d_r a_r")
br = Param(name="b_r", description="Birth Rate")
dr = Param(name="d_r", description="")
flow_in = Flow(name="birth", eq="b_r * P(t)")
flow_out = Flow(name="death", eq="d_r * P(t)")
Ps = Stock(name="P", flow_in=flow_in, flow_out=flow_out)

ar = Param(name="a_r", description="Tech Growth Rate")
flow_in_a = Flow(name="tech_incr", eq="a_r * A(t)")
As = Stock(name="A", flow_in=flow_in_a)

mod = Module(name="Econ", stocks=[Ps, As], params=[br, dr, ar])
sys = System(name="Solow", modules=[mod])

tspan = np.arange(0,50,1)
init_vals={
    fP(0):1,
    fA(0):2
}
params_vals={
    b_r: 0.02,
    d_r: 0,
    a_r: 0.03
}
prob = Problem(
    name="Run 1", 
    t_span=tspan, 
    system=sys,  
    init_vals=init_vals, 
    param_vals=params_vals, 
    policy_vals={}
)

def start():
    res = prob.solve()
    print(res)
