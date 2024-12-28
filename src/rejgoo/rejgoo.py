from parser import parser
from solver import solve_systems

text ='''
y+x=49
a + b + c = 45
z + z**2 = 65

a + 2*b = 30
b + c = 9
z + w = 44
x**2+19=y**3

'''

ordered_eqs, ordered_vars = parser(text)
res = solve_systems(ordered_eqs, ordered_vars)
print(res)