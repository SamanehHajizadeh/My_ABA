import functools

import networkx as nx

from .abadisputetree import AbaDisputeTree
from .aba_graph import ABA_Graph


class ABA_framework():
    def __init__(self):
        self.symbols = []
        self.rules = []
        self.assumptions = []
        self.contraries = dict()
        self.nonassumptions = []

        self.arguments = []
        self.potential_arguments = []
        self.dispute_trees = []

    """
    Each assumption must have a contrary.
    """

    def flag_for_contrary(self):
        all_assumption_have_contrary = True
        for assumption in self.assumptions:
            if assumption not in self.contraries.keys():
                all_assumption_have_contrary = False
                break
        return all_assumption_have_contrary

    """    
    Infer_assumptions to extract the assumptions from the contraries
    """

    def extract_assumptions_from_contraries(self):
        self.nonassumptions = list(self.symbols)

        for key in self.contraries:
            if key not in self.assumptions:
                self.assumptions.append(key)

        for assumption in self.assumptions:
            if assumption in self.nonassumptions:
                self.nonassumptions.remove(assumption)

    """
    To construct the argument trees
    Check if all assumptions have its contrary
    It append instances of ABA_Graph objects to “potential_arguments” and appended to “arguments” if satisfy criteria being an actual argument  
    """

    def construct_arguments(self):
        if not self.flag_for_contrary():
            raise Exception("All assumptions must have contrary")

        for symbol in self.symbols:
            potential_argument = ABA_Graph(self, symbol)
            for i in range(len(potential_argument.graphs)):
                self.potential_arguments.append((potential_argument, i))
                if potential_argument.is_actual_argument(i):
                    self.arguments.append((potential_argument, i))

    def generates_instances_of_Dispute_Tree_and_append_to_dispute_trees(self):
        if not self.flag_for_contrary():
            raise Exception("All assumptions must have contrary")

        args_grounded = {}

        for argument, i in self.arguments:
            if argument:
                if argument.root not in args_grounded:
                    args_grounded[argument.root] = False
                if args_grounded[argument.root]:
                    print("Skipping DT ", argument.root, i)
                    continue

                self.append_to_dispute_trees(args_grounded, argument, i)
        #self.__determine_dispute_tree_is_complete()

    def append_to_dispute_trees(self, args_grounded, argument, i):
        dt = AbaDisputeTree(self, argument, i)
        self.dispute_trees.append(dt)
        args_grounded[argument.root] = functools.reduce(lambda x, y: x or y, dt.is_grounded)

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
            for l, graph in enumerate(tree.graphs):
                complete = False
                if tree.is_admissible[l]:
                    print("is tree admissible:", tree.is_admissible[l])
                    complete = True
                    if not tree.is_grounded[l]:

                        # x = all arguments root_ that can attack
                        # y = all arguments that can be attacked by x
                        # Complete =  If ALL y are inside root_
                        attackables_by_root = self.__get_arguments_attackable(tree.root_arg)

                        defendable_arguments = []
                        for attackable, i in attackables_by_root:
                            defendable_arguments.extend(self.__get_arguments_attackable(attackable))

                        all_in_argument = True
                        for argument, i in defendable_arguments:
                            if argument.root not in tree.root_arg.graphs[i].nodes():
                                all_in_argument = False
                                break
                        complete = all_in_argument
                tree.is_complete[l] = complete

    def get_argument(self, symbol, index=0, allow_potential=False):
        source = self.arguments
        if allow_potential:
            source = self.potential_arguments
        argument = [x for x in source if x[0].root == symbol and x[1] == index]

        if len(argument) > 0:
            return argument[0]
        return None, None

    def get_dispute_tree(self, symbol, index=0):
        dispute_tree = [x for x in self.dispute_trees if x.root_arg.root == symbol and x.arg_index == index]
        if len(dispute_tree) > 0:
            return dispute_tree[0]
        return None

    def get_combined_argument_graph(self):
        combined = nx.DiGraph()
        for potential_argument, index in self.potential_arguments:
            symbol = potential_argument.root
            argument, i = self.get_argument(symbol, index=index, allow_potential=True)

            if argument is None:
                arg_root = "τ"
                combined.add_node(symbol + "_" + arg_root, group=arg_root)
                continue

            arg_root = argument.root
            for node in argument.graphs[i].nodes():
                if node is None:
                    node = "τ"
                combined.add_node(node + "_" + arg_root, group=arg_root)

            for edge in argument.graphs[i].edges_iter():
                edge0, edge1 = edge
                if edge0 is None:
                    edge0 = "τ"
                if edge1 is None:
                    edge1 = "τ"
                combined.add_edge(edge0 + "_" + arg_root, edge1 + "_" + arg_root)

        return combined
