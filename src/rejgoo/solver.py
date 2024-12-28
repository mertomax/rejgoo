from newt_raph import solve_eqs
import re

def solve_systems(ordered_eqs, ordered_vars):
    systems_results = {}

    for system_eqs, system_vars in zip(ordered_eqs, ordered_vars):
        results = solve_system(system_eqs, system_vars)
        systems_results.update(results)

    systems_results = {key:float(value) for key, value in systems_results.items()}

    return systems_results

def insert_solved_vars(eqs, solved_vars):
    masked_eqs = []

    for eq in eqs:
        for var_id, var_val in solved_vars.items():
            mask = r'(?<!\w)({})(?!\w)'.format(var_id)
            eq = re.sub(mask, str(var_val), eq)
        masked_eqs.append(eq)

    return masked_eqs

def solve_system(system_eqs, system_vars):
    system_results = {}

    for sub_eqs, sub_vars in zip(system_eqs, system_vars):
        sub_inserted_eqs = insert_solved_vars(sub_eqs, system_results)
        unsolved_vars = [var for var in sub_vars if var not in system_results.keys()]
        results = solve_sub_system(sub_inserted_eqs, unsolved_vars)
        system_results.update(results)

    return system_results

def solve_sub_system(eqs, vars_ids):
    values = solve_eqs(eqs, vars_ids)
    results = {key:value for key, value in zip(vars_ids, values)}

    return results
