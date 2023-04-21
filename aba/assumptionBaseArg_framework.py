class AbaFramework:
    def __init__(self):
        self.symbols = []
        self.rules = []
        self.assumptions = []
        self.contraries = dict()
        self.not_assumptions = []

        self.arguments = []
        self.potential_arguments = []
        self.dispute_trees = []

    def flag_for_contrary(self):
        all_assumption_have_contrary = True
        for assumption in self.assumptions:
            if assumption not in self.contraries.keys():
                all_assumption_have_contrary = False
                break
        return all_assumption_have_contrary

    def extract_assumptions_from_contraries(self):
        self.not_assumptions = list(self.symbols)

        for key in self.contraries:
            if key not in self.assumptions:
                self.assumptions.append(key)

        for assumption in self.assumptions:
            if assumption in self.not_assumptions:
                self.not_assumptions.remove(assumption)

        print("Assumptions", self.assumptions)
        print("Not a assumptions", self.not_assumptions)

        """
        Given an argument, which other arguments it can attack?
        """

    def __get_arguments_attackable(self, arg):
        attackables = []
        for argument, i in self.arguments:
            attackable = arg.root in argument.assumptions[i].values()

            if attackable:
                attackables.append((argument, i))
        return attackables

    def __determine_dispute_tree_is_complete(self):
        for tree in self.dispute_trees:
            for tree_idx, graph in enumerate(tree.graphs):
                complete = False
                if tree.is_admissible[tree_idx]:
                    complete = True
                    if not tree.is_grounded[tree_idx]:

                        # 1. Get all arguments root_arg can attack --> assign as x
                        # 2. Get all arguments that can be attacked by x --> assign as y
                        # 3. If ALL y inside root_arg, then complete
                        attackables_by_root = self.__get_arguments_attackable(tree.root_arg)
                        self.admisible_tree_definition_rule()

                        defendable_arguments = []
                        for attackable, i in attackables_by_root:
                            defendable_arguments.extend(self.__get_arguments_attackable(attackable))
                        # Saman attach
                        all_in_argument = True
                        for argument, i in defendable_arguments:
                            if argument.root not in tree.root_arg.graphs[i].nodes():
                                all_in_argument = False
                                break
                        complete = all_in_argument

                tree.is_complete[tree_idx] = complete
                print("Dispute is complete: %s", tree.root_arg.root, tree_idx,
                      tree.is_complete[tree_idx])

    def admisible_tree_definition_rule(self):
        pass

    def get_argument(self, symbol, index=0, allow_potential=False):
        source = self.arguments
        if allow_potential:
            source = self.potential_arguments
        argument = [x for x in source if x[0].root == symbol and x[1] == index]

        if len(argument) > 0:
            return argument[0]
        return None, None
