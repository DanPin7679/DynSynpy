from enum import Enum

class ProblemType(str, Enum):
    discrete = 'discrete'

class Solver(str, Enum):
    custom = 'custom'  
    sympy = 'sympy'
