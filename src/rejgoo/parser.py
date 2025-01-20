from itertools import combinations
import re

#-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-#

def eqs_extractor(text):
    """
    This function gets input equations as a single text,
    and returns separated equations as a list.

    Parameters:
    text (str): input equations

    Returns:
    list: extracted equations
    """
    
    eqs = text.replace(' ', '')
    eqs = eqs.split('\n')
    eqs = [i for i in eqs if i !='']
    return eqs

def is_number(x):
    try:
        float(x)
        return True
    except:
        return False

def var_extractor(eq):
    """
    This function gets an equation as a string,
    and returns existing variables in the equation as a list

    Parameters:
    eq (str): input equation

    Returns:
    list: extracted variables.
    """

    eq.replace(' ', '')
    math_funs = ('sin', 'asin', 'sinh', 'asinh',
                 'cos', 'cosa', 'cosh', 'acosh',
                 'tan', 'atan', 'tanh', 'atanh',
                 'cot', 'acot', 'coth', 'acoth',
                 'exp', 'log')

    for math_fun in math_funs:
        mask = r'(^|[\+\-*/=(]){}\('.format(math_fun)
        eq = re.sub(mask, ' ', eq)
    
    math_ops = ('+', '-', '*', '/', '=', '(', ')')
    for op in math_ops:
        eq = eq.replace(op, ' ')
    variables = eq.split(' ')
    variables = [i for i in variables if i != '']
    variables = [i for i in variables if not is_number(i)]
    
    for var in variables:
        if not var.isidentifier():
            raise ValueError('{} is not a valid variable name, be pythonic!'.format(var))
    
    return set(variables)

#-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-#

def find_eqs_systems_labels(eqs, variables):
    """
    This function gets a list of equations,
    and a list of variables corresponding to each equation.

    Then the function tries to group equations that have common variables together. 
    And label each equation with an integer that shows which group the equation belongs to.

    Parameters:
    eqs (list): A list that contains all equations as string.
    variables (list): A list of lists! The inner list contains variables as strings.
        The i_th inner list contains variables of the i_th eq in the eqs.

    Returns:
    list: A list which its i_th element determines the group's label of i_th eq in eqs.
    int: Number of total found groups 
    """

    def track(var, label):
        nonlocal tracked_vars, group_labels
    
        tracked_vars.append(var)
        
        for idx, var_set in enumerate(variables):
            if var in var_set:
                group_labels[idx] = label
                for next_var in var_set:
                    if next_var not in tracked_vars:
                        track(next_var, label)


    group_labels = [None for i in variables]

    total_groups = 0
    tracked_vars = []

    all_vars = []
    for var_set in variables:
        all_vars.extend(var_set)
    all_vars = list(set(all_vars))
    all_vars.sort()
            
    for var in all_vars:
        if var not in tracked_vars:
            label = total_groups
            total_groups += 1
            track(var, label)

    return group_labels, total_groups

def seperate_eqs_systems(eqs, variables, group_labels, total_groups):
    """
    This function gets a bag of equations and tries to
    separate them into different systems of equations,
    with no common variable
    """
    eqs_sets = []
    var_sets = []

    for idx in range(total_groups):
        sub_eq = []
        sub_vars = []
        for eq, var_set, label in zip(eqs, variables, group_labels):
            if idx == label:
                sub_eq.append(eq)
                sub_vars.append(list(var_set))
        eqs_sets.append(sub_eq)
        var_sets.append(sub_vars)

    for eqs_set, var_set in zip(eqs_sets, var_sets):
        
        merged_vars = []
        for variables in var_set:
            merged_vars.extend(variables)
        merged_vars = set(merged_vars)

        if len(eqs_set) != len(merged_vars):
            print('The folwing system of equations consists of {} equations and {} variables!'\
                  .format(len(eqs_set), len(merged_vars)))
            print('It can not be solved!\n')
            for eq in eqs_set:
                print(eq)
            raise Warning('variables and equations does not match!')

    return eqs_sets, var_sets

#-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-#

def cross_var(combined_vars, var_set):
    """
    In eqs_order_idx function, When a sub-system of equations is found,
    the variable of the found sub-system needs to be omitted
    from the list of total variables in the system.
    This function does it and, omits the sub-system variables from
    the list of all variables.
    
    """
    results = []
    
    for sub_var in var_set:
        sub_var = [i for i in sub_var if i not in combined_vars]
        results.append(sub_var)

    return results


def eqs_order_idx(var_set):
    """
    This function provides labels, that show the priority of each equation.
    The labels will be used in ordered_eqs_vars function.
    """
    var_set = var_set[:]
    
    priority = [None for i in var_set]
    priority_count = 0
    
    var_set_idx = [i for i in range(len(var_set))]
    
    max_size = len(var_set)
    comb_size = 1
    
    while None in priority:
        
        if comb_size > max_size:
            raise Exception('variables and equations does not match!')
        
        combs = combinations(var_set_idx, comb_size)
        
        for comb in combs:
            combined_vars = []
            for i in comb:
                combined_vars.extend(var_set[i])
            combined_vars = set(combined_vars)
            if len(combined_vars) == comb_size:
                var_set = cross_var(combined_vars, var_set)
                comb_size = 0

                for i in comb:
                    priority[i] = priority_count
                    
                priority_count += 1
                break
        
        comb_size += 1
    return priority, priority_count

def ordered_eqs_vars(eqs_sets, var_sets):
    """
    When there is a system of equations like:

    X + Y = Z
    X + Y = 5
    X  + 1 = 2

    We can solve all three of them simultaneously.
    But the solving process will take a lot of time,
    despite the simplisity of the system!

    A better aporoah is to solve it step by step!
    At first, we souled solve (X  + 1 = 2). now that we have
    found the value of X, we cansolve (X + Y = 5).
    and after all (X + Y = Z) can be solved.

    Solving equations by order can improve solving time!

    This function tries to order the input system of equations,
    with returned label list from eqs_order_idx function.
    """

    ordered_eqs = []
    ordered_vars = []

    for eqs_set, var_set in zip(eqs_sets, var_sets):
        sub_ord_eqs = []
        sub_ord_vars = []
        
        priority, priority_count = eqs_order_idx(var_set)
        for i in range(priority_count):
            sub_eqs = []
            sub_vars = []
            for idx, p_label in enumerate(priority):
                if p_label == i:
                    sub_eqs.append(eqs_set[idx])
                    sub_vars.extend(var_set[idx])
                    
            sub_ord_eqs.append(sub_eqs)
            sub_ord_vars.append(list(set(sub_vars)))
            
        ordered_eqs.append(sub_ord_eqs)
        ordered_vars.append(sub_ord_vars)

    return ordered_eqs, ordered_vars

#-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-#
