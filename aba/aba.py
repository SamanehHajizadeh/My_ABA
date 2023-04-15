from .aba_graph import ABA_Graph
from .aba_dispute_tree import ABA_Dispute_Tree
from .aba_constants import *
import networkx as nx
import logging
import functools


class ABA():
    def __init__(self):
        self.symbols = []
        self.rules = []
        self.assumptions = []
        self.contraries = dict()
        self.nonassumptions = []

        self.arguments = []
        self.potential_arguments = []
        self.dispute_trees = []

    def is_all_assumption_have_contrary(self):
        """
        Each assumption must have a contrary.
        """
        all_assumption_have_contrary = True
        for assumption in self.assumptions:
            if assumption not in self.contraries.keys():
                all_assumption_have_contrary = False
                break
        return all_assumption_have_contrary

    #infer_assumptions to extract the assumptions from the contraries
    def extract_assumptions_from_contraries(self):
        self.nonassumptions = list(self.symbols)

        for key in self.contraries:
            if key not in self.assumptions:
                self.assumptions.append(key)

        for assumption in self.assumptions:
            if assumption in self.nonassumptions:
                self.nonassumptions.remove(assumption)

    #To construct the argument trees
    #Check if all assumptions have its contrary
    #It append instances of ABA_Graph objects to “potential_arguments” and appended to “arguments” if satisfy criteria being an actual argument
    def construct_arguments(self):
        if not self.is_all_assumption_have_contrary():
            raise Exception("All assumptions must have contrary")

        for symbol in self.symbols:
            potential_argument = ABA_Graph(self, symbol)
            for i in range(len(potential_argument.graphs)):
                self.potential_arguments.append((potential_argument, i))
                if potential_argument.is_actual_argument(i):
                    self.arguments.append((potential_argument, i))

    def generates_instances_of_Dispute_Tree_and_append_to_dispute_trees(self):
        if not self.is_all_assumption_have_contrary():
            raise Exception("All assumptions must have contrary")

        args_grounded = {}

        for argument, i in self.arguments:
            if argument:
                if argument.root not in args_grounded:
                    args_grounded[argument.root] = False
                if args_grounded[argument.root]:  # if grounded, then also must be admissible
                    logging.debug("Skipping DT <%s, %d>", argument.root, i)
                    # Skipping DT generation if previously a grounded DT has been found
                    continue

                print("ABA_Dispute_Tree <%s>" % argument)
                self.append_to_dispute_trees(args_grounded, argument, i)

        print("__determine_dispute_tree_is_ideal")
        self.__determine_dispute_tree_is_ideal()

        print("__determine_dispute_tree_is_complete")
        self.__determine_dispute_tree_is_complete()

    def append_to_dispute_trees(self, args_grounded, argument, i):
        dt = ABA_Dispute_Tree(self, argument, i)
        self.dispute_trees.append(dt)
        args_grounded[argument.root] = functools.reduce(lambda x, y: x or y, dt.is_grounded)

    def __determine_dispute_tree_is_ideal(self):
        for tree in self.dispute_trees:
            for tree_idx, graph in enumerate(tree.graphs):
                ideal = False
                if tree.is_admissible[tree_idx]:
                    ideal = True
                    for node in graph.nodes(data=True):
                        if node[1]['label'] == DT_OPPONENT:
                            opponent_dispute_tree = self.get_dispute_tree(node[0], tree.arg_index)
                            if opponent_dispute_tree and opponent_dispute_tree.is_admissible:
                                ideal = False
                                break
                tree.is_ideal[tree_idx] = ideal
                logging.debug("Dispute Tree <%s, %s> is ideal: %s", tree.root_arg.root, tree_idx,
                              tree.is_ideal[tree_idx])

    def __get_arguments_attackable(self, arg):
        """
        Given an argument, which other arguments it can attack?
        """
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
                    if not tree.is_grounded[tree_idx]:  # if tree is grounded, it is guaranteed to be complete

                        # 1. Get all arguments root_arg can attack --> assign as x
                        # 2. Get all arguments that can be attacked by x --> assign as y
                        # 3. If ALL y inside root_arg, then complete
                        attackables_by_root = self.__get_arguments_attackable(tree.root_arg)
                        # Note: since root_arg is admissible, then it is conflict-free, i.e. root_arg is guaranteed not to be inside attackables_by_root

                        defendable_arguments = []
                        for attackable, i in attackables_by_root:
                            defendable_arguments.extend(self.__get_arguments_attackable(attackable))

                        all_in_argument = True
                        for argument, i in defendable_arguments:
                            if argument.root not in tree.root_arg.graphs[i].nodes():
                                all_in_argument = False
                                break
                        complete = all_in_argument
                        # logging.debug("DT<%s> Defendable arguments: %s", tree.root_arg.root, defendable_arguments)

                tree.is_complete[tree_idx] = complete
                logging.debug("Dispute Tree <%s, %s> is complete: %s", tree.root_arg.root, tree_idx,
                              tree.is_complete[tree_idx])

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
