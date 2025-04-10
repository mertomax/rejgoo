from .newt_raph import solve_eqs
from .parser import var_extractor, thermo_finder
import re
from CoolProp import CoolProp


def coolprop_formater(eqs, map_dict):

    formated_eqs = []

    for eq in eqs:
        for pattern, formated_pattern in map_dict.items():
            if pattern in eq:
                eq = eq.replace(pattern, formated_pattern)
        formated_eqs.append(eq)

    return formated_eqs

def thermo_val_initializer(eqs, solved_vars):

    thermo_init_vals = {}
    
    if len(eqs) != 1:
        return {}
    else:
        eq = eqs[0]

    from .rejgoo import eqs as eqs_solver

    CP_fluids = CoolProp.get_global_param_string("FluidsList").split(',')
    CP_fluids.append('HumidAir')
    CP_fluids_lower_to_origin = {fluid.lower():fluid for fluid in CP_fluids}
    
    thermo_funs_dict = thermo_finder(eq)
    for finded_patern, all_params in thermo_funs_dict.items():
        property = all_params['property']

        parsed_fluid = all_params['fluid']
        if parsed_fluid.lower() not in CP_fluids_lower_to_origin.keys():
            raise Exception('{} is not a valid fluid name!'.format(parsed_fluid))
        fluid = CP_fluids_lower_to_origin[parsed_fluid.lower()]
        if fluid == 'HumidAir':
            fluid = 'Air'

        params_args = all_params['params_args']

        for param, arg in params_args.items():
            print(arg, type(arg), '---')
            arg = insert_solved_vars([arg], solved_vars)[0]
            print(arg, '=====')
            print(insert_solved_vars([arg], solved_vars))
            if len(var_extractor(arg)) == 1:
                min_val = CoolProp.PropsSI('{}min'.format(param), fluid)
                max_val = CoolProp.PropsSI('{}max'.format(param), fluid)
                avr_val = (min_val + max_val) / 1
                results = eqs_solver('{} = {}'.format(avr_val, arg), verbose=False)
                thermo_init_vals.update(results.solved_vars)


    return thermo_init_vals

def insert_solved_vars(eqs, solved_vars):
    """
    IF the value of a variable is optimized,
    this function replaces identifiers of variables with it's values.
    """
    masked_eqs = []

    for eq in eqs:
        for var_id, var_val in solved_vars.items():
            mask = r"""(?<![\w_'"]){}(?![\w_'"])""".format(var_id)
            eq = re.sub(mask, str(var_val), eq)
        masked_eqs.append(eq)

    return masked_eqs

def solve_system(system_eqs, system_vars, coolprop_map_dict, **kwargs):
    """
    This function solves a system of equations,
    which is part of all systems of equations.
    The system may contain several sub-systems that should be solved by order.
    """
    system_results = {}
    system_residuals = []

    for sub_eqs, sub_vars in zip(system_eqs, system_vars):
        thermo_init_vals = thermo_val_initializer(sub_eqs, system_results)
        kwargs['thermo_init_vals'] = thermo_init_vals
        sub_eqs = coolprop_formater(sub_eqs, coolprop_map_dict)
        sub_inserted_eqs = insert_solved_vars(sub_eqs, system_results)
        unsolved_vars = [var for var in sub_vars if var not in system_results.keys()]
        results, cost_residuals = solve_sub_system(sub_inserted_eqs, unsolved_vars, **kwargs)
        system_results.update(results)
        system_residuals.append(cost_residuals)

    return system_results, system_residuals

def solve_sub_system(eqs, vars_ids, **kwargs):
    """
    This solves a sub-system of equations,
    and returns the results.
    """
    
    values, cost_residuals = solve_eqs(eqs, vars_ids, **kwargs)
    results = {key:value for key, value in zip(vars_ids, values)}

    return results, cost_residuals
