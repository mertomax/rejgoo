if __name__ == '__main__':
    from parser import parser
    from solver import solve_systems

    eqs = 'x**2 + 3*x = 25'
    a, b = parser(eqs)
    res = solve_systems(a, b, init_vals={'x':-10})
