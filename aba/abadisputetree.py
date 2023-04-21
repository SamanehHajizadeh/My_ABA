import functools
import pickle

import networkx as nx
import ujson

from .constant_params import *


class AbaDisputeTree:
    """
    ABA_Dispute_Tree
    Vertices: <argument + label>
    Edges: attacks
    """

    def __init__(self, aba=None, root_arg=None, arg_index=0):
        self.graphs = [nx.DiGraph()]

        self.root_arg = root_arg
        self.arg_index = arg_index
        self.__aba = aba

        self.__history = [[]]
        self.__depth = [0]

        self.__cache = {}

        self.__max_index = 0
        self.graphs[0].add_node(root_arg.root)
        self.__add_label(0, root_arg, DT_PROPONENT)
        self.__depth[0] += 1

        self.__found_grounded = False

        self.is_grounded = [True]
        self.is_admissible = [True]
        self.is_complete = [None]
        self.is_ideal = [None]
        self.__propagate_tree_proponent(0, root_arg)

    def __handle_leaf(self):
        self.__found_grounded = functools.reduce(lambda x, y: x or y, self.is_grounded)

    def __propagate_tree_proponent(self, index, node):
        """
        Attack by opponents
        """
        global level_history_copy, level_is_grounded_copy, level_is_admissible_copy, level_depth_copy, level_graphs_copy
        if self.__found_grounded:
            return self.global_level()

        if len(node.assumptions) > 1:
            level_graphs_copy = pickle.dumps(self.graphs[index], -1)
            level_history_copy = ujson.dumps(self.__history[index])
            level_depth_copy = ujson.dumps(self.__depth[index])
            level_is_grounded_copy = ujson.dumps(self.is_grounded[index])
            level_is_admissible_copy = ujson.dumps(self.is_admissible[index])

        for idx, assumptions in enumerate(
                node.assumptions):
            index_used = index
            if idx > 0:
                self.graphs.append(pickle.loads(level_graphs_copy))

                self.__history.append(ujson.loads(level_history_copy))
                self.__depth.append(ujson.loads(level_depth_copy))
                self.is_grounded.append(ujson.loads(level_is_grounded_copy))
                self.is_admissible.append(ujson.loads(level_is_admissible_copy))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__max_index += 1
                index_used = self.__max_index

            for assumption, symbol in assumptions.items():
                opponent_node, i = self.__aba.get_argument(symbol, 0)

                if opponent_node is None:
                    self.__handle_leaf()
                    if self.__found_grounded:
                        return self.global_level()
                    continue

                self.graphs[index_used].add_edge(node.root, opponent_node.root,
                                                 text_label="Opponent node <%s, %d> attacking assumption <%s> of Proponent node <%s, %d>" % (
                                                     opponent_node.root, i, assumption, node.root, index))
                print("Opponent node", opponent_node.root, "attacking assumption ", assumption, " of Proponent node ",
                      node.root)
                self.__add_label(index_used, opponent_node, DT_OPPONENT, assumption_index=0)

                if self.__is_infinity(index_used, opponent_node, DT_OPPONENT):
                    break

                self.__depth[index_used] += 1
                self.__history[index_used].append([opponent_node.root, DT_OPPONENT])
                self.__propagate_tree_opponent(index_used, opponent_node)
                self.__history[index_used].pop()
                self.__depth[index_used] -= 1

    def global_level(self):
        return

    """
    Attack by proponent
    one ProponentNode to one OpponentNode
    """

    def __propagate_tree_opponent(self, index, node):

        global level_history_copy, level_depth_copy, level_is_grounded_copy, level_is_admissible_copy, level_graphs_copy
        if self.__found_grounded:
            return self.global_level()

        if len(node.assumptions) > 1:
            level_graphs_copy = pickle.dumps(self.graphs[index], -1)
            level_history_copy = ujson.dumps(self.__history[index])
            level_depth_copy = ujson.dumps(self.__depth[index])
            level_is_grounded_copy = ujson.dumps(self.is_grounded[index])
            level_is_admissible_copy = ujson.dumps(self.is_admissible[index])

        for idx, assumptions in enumerate(node.assumptions):
            index_used = index
            if idx > 0:
                self.graphs.append(pickle.loads(level_graphs_copy))
                self.__history.append(ujson.loads(level_history_copy))
                self.__depth.append(ujson.loads(level_depth_copy))
                self.is_grounded.append(ujson.loads(level_is_grounded_copy))
                self.is_admissible.append(ujson.loads(level_is_admissible_copy))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__max_index += 1
                index_used = self.__max_index

            for assumption, symbol in assumptions.items():
                proponent_node, i = self.__aba.get_argument(symbol, 0)
                if proponent_node is None:
                    self.__handle_leaf()
                    if self.__found_grounded:
                        return self.global_level()
                    continue

                if (proponent_node.root, i) in self.__cache:
                    cached_data = self.__cache[(proponent_node.root, i)]
                    tree_from_cache = pickle.loads(cached_data["tree"])

                    self.graphs[index_used] = nx.compose(self.graphs[index_used], tree_from_cache)
                    self.is_grounded[index_used] &= cached_data["is_grounded"]
                    self.is_admissible[index_used] &= cached_data["is_admissible"]
                    continue

                self.graphs[index_used].add_edge(node.root, proponent_node.root,
                                                 text_label="Proponent node <%s, %d> attacking assumption <%s> of Opponent node <%s, %d>" % (
                                                     proponent_node.root, i, assumption, node.root, index))
                self.__add_label(index_used, proponent_node, DT_PROPONENT, assumption_index=0)

                if self.__is_infinity(index_used, proponent_node, DT_PROPONENT):
                    break

                self.__depth[index_used] += 1
                self.__history[index_used].append([proponent_node.root, DT_PROPONENT])
                self.__propagate_tree_proponent(index_used, proponent_node)
                self.__history[index_used].pop()
                self.__depth[index_used] -= 1

                break

    def __is_infinity(self, index, node, label):

        value = [node.root, label] in self.__history[index]
        if value:
            self.is_grounded[index] = False

        return value

    def __add_label(self, index, node, label, assumption_index=0):
        self.graphs[index].node[node.root]['label'] = label
        self.graphs[index].node[node.root]['text_label'] = "(%s) Argument %s" % (label, node.root)

        if len(node.assumptions[assumption_index]) > 0:
            self.graphs[index].node[node.root]['text_label'] += "\nwith assumption(s): %s" % (
                ", ".join(node.assumptions[assumption_index]))
            print(self.graphs[index].node[node.root])
            print("lable:", label, "\nnode.root:", node.root)

        if 'depth' not in self.graphs[index].node[node.root]:
            print(self.graphs[index].node[node.root])
            self.graphs[index].node[node.root]['depth'] = self.__depth[index]
