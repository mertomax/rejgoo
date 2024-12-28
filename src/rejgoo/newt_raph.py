import numpy as np
import re

def eq_to_cost(eqs):
    cost_fs = []
    for idx, eq in enumerate(eqs):
        equal_loc = eq.find('=')
        cost = eq[:equal_loc] + '-(' + eq[equal_loc+1:] + ')'
        cost_fs.append(cost)

    return cost_fs


def residual(vars_val, cost_fs, vars_masks):
    res = []
    for cost in cost_fs:
        for var_m, var_val in zip(vars_masks, vars_val):
            cost = re.sub(var_m, str(var_val), cost)
        res.append(eval(cost))
    
    return np.array(res)


def deriv(vars_val, cost_fs, vars_masks):
    res = np.zeros((len(cost_fs), len(vars_val)))

    for var_idx, var_val in enumerate(vars_val):
        vars_val_plus = vars_val.copy()
        vars_val_plus[var_idx] = vars_val_plus[var_idx] + 0.00001
        before = residual(vars_val, cost_fs, vars_masks)
        after = residual(vars_val_plus, cost_fs, vars_masks)
        der = (after - before) / 0.00001
        res[:, var_idx] = der

    return res


def newtraph(vars_val, cost_fs, vars_masks, max_iter=1000):
    for _ in range(max_iter):
        a = deriv(vars_val, cost_fs, vars_masks)
        b = residual(vars_val, cost_fs, vars_masks)
        delt = (np.linalg.inv(a) @ b)
        vars_val -= delt
    
    return vars_val

def solve_eqs(eqs, vars_id, init_vals={}):
    vars_val = [init_vals.get(i, np.random.rand())
            for i in vars_id]
    vars_val = np.array(vars_val)

    vars_masks = [r'(?<!\w)({})(?!\w)'.format(var_id) for var_id in vars_id]
    cost_fs = eq_to_cost(eqs)
    results = newtraph(vars_val, cost_fs, vars_masks)

    return results
