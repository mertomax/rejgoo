from itertools import combinations


#-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-#

def eqs_extractor(text):
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

    return eqs_sets, var_sets


#-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-#

def cross_var(combined_vars, var_set):
    results = []
    
    for sub_var in var_set:
        sub_var = [i for i in sub_var if i not in combined_vars]
        results.append(sub_var)

    return results


def eqs_order_idx(var_set):
    var_set = var_set[:]
    
    priority = [None for i in var_set]
    priority_count = 0
    
    var_set_idx = [i for i in range(len(var_set))]
    
    max_size = len(var_set)
    comb_size = 1
    
    while None in priority:
        
        if comb_size > max_size:
            raise Exception('variables and equations does not match')
        
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

def parser(text):
    eqs = eqs_extractor(text)
    variables = [var_extractor(eq) for eq in eqs]

    group_labels, total_groups = find_eqs_systems_labels(eqs, variables)
    eqs_sets, var_sets = seperate_eqs_systems(eqs, variables,
                                              group_labels, total_groups)

    ordered_eqs, ordered_vars = ordered_eqs_vars(eqs_sets, var_sets)

    return ordered_eqs, ordered_vars

#-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-#


text ='''
b + c = 8
x + y + z = 4
x + y = 3

z + a = 6
x = 1
a + b = 9


'''

ordered_eqs, ordered_vars = parser(text)
