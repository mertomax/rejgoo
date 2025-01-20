from .parser import *
from .solver import *

class eqs():
    def __init__(self, text, do_parse=True, do_solve=True, **kwargs):
        self.text = text

        settings_kws = ('verbose', 'init_vals', 'max_iter', 'learning_rate')
        
        for key in kwargs.keys():
            if key not in settings_kws:
                raise ValueError('{} is not a valid keword argument!'.format(key))
            
        self.settings = kwargs
        self.verbose = kwargs.get('verbose', True)

        if do_parse:
            self.parse()

        if do_solve:
            self.vars_vals = self.solve()

    def parse(self):
        eqs = eqs_extractor(self.text)
 
        eqs_vars = [var_extractor(eq) for eq in eqs]
        
        all_vars = []
        for eq_vars in eqs_vars:
            all_vars.extend(eq_vars)
        all_vars = set(all_vars)

        if self.verbose:
            print('Total number of equations: {}'.format(len(eqs)))
            print('Total number of variables: {}'.format(len(all_vars)))

        if len(eqs) != len(all_vars):
            raise Warning('Total Number of equations and variables does not match!')

        group_labels, total_groups = find_eqs_systems_labels(eqs, eqs_vars)
        if self.verbose:
            print('Number of isolated systems of equations: {}\n'.format(total_groups))
            
        eqs_sets, var_sets = seperate_eqs_systems(eqs, eqs_vars,
                                                  group_labels, total_groups)

        self.ordered_eqs, self.ordered_vars = ordered_eqs_vars(eqs_sets, var_sets)

        if self.verbose:
            for system_idx, system in enumerate(self.ordered_eqs):
                print('system number: _{}_'.format(system_idx+1))
                print('number of equations in this system: {}\n'.format(len(eqs_sets[system_idx])))
                print('solve\norder       equations')
                print('--------------------------------------------------------------------')
                for sub_system_idx, sub_system in enumerate(system):
                    for eq in sub_system:
                        print('{:4d}       {}'.format(sub_system_idx+1, eq))
                print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_\n')


    def solve(self):

        systems_results = {}

        for system_eqs, system_vars in zip(self.ordered_eqs, self.ordered_vars):
            results = solve_system(system_eqs, system_vars, **self.settings)
            systems_results.update(results)

        systems_results = {key:float(value) for key, value in systems_results.items()}

        if self.verbose:
            print('Values of variables:\n')
            for key, value in systems_results.items():
                print('{}:    {}'.format(key, value))

        return systems_results
