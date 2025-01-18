from .parser import *
from .solver import *

class eqs():
    def __init__(self, text, do_parse=True, do_solve=True, **kwargs):
        self.text = text
        self.kwargs = kwargs
        self.verbose = kwargs.get('verbose', False)

        if do_parse:
            self.parse()

        if do_solve:
            self.vars_vals = self.solve()

    def parse(self):
        eqs = eqs_extractor(self.text)
        variables = [var_extractor(eq) for eq in eqs]

        group_labels, total_groups = find_eqs_systems_labels(eqs, variables)
        eqs_sets, var_sets = seperate_eqs_systems(eqs, variables,
                                                  group_labels, total_groups)

        self.ordered_eqs, self.ordered_vars = ordered_eqs_vars(eqs_sets, var_sets)

        if self.verbose:
            print('Total number of equations: {}'.format(len(eqs)))
            print('Total number of variables: {}'.format(len(variables)))

            print('Number of isolated groups of equations: {}'.format(total_groups))

    def solve(self):

        settings_kws = ('init_vals',)
        settings = {key:value for key, value in self.kwargs.items() if key in settings_kws}
        #print(settings)
        systems_results = {}

        for system_eqs, system_vars in zip(self.ordered_eqs, self.ordered_vars):
            results = solve_system(system_eqs, system_vars, **settings)
            systems_results.update(results)

        systems_results = {key:float(value) for key, value in systems_results.items()}
        return systems_results
