import networkx as nx
import ujson
import pickle


class ABA_Graph():
    """
    An ABA_Graph object is an argument, i.e. a node, supported by sentences & assumptions
    """

    def __init__(self, aba=None, root=None):
        self.graphs = []

        self.__history = [[]]
        self.__is_cyclical = [False]

        self.assumptions = [{}]
        self.is_conflict_free = [None]
        self.is_stable = [None]

        self.root = root
        self.__aba = aba
        self.__max_index = 0

        self.graphs.append(nx.DiGraph())
        self.__branches = 1

        self.graphs[0].add_node(root)
        self.__history[0].append(root)
        self.__propagate(0, root)
        self.__history[0].pop()

        self.__sort_graphs()

        self.__propagate_assumptions()
        self.__is_conflict_free()
        self.__is_stable()

    def __sort_graphs(self):
        graphs_and_is_cyclical = [[x, False] for x in self.graphs]
        for i, item in enumerate(graphs_and_is_cyclical):
            item[1] = self.__is_cyclical[i]

        graphs_and_is_cyclical.sort(key=self.__key_graph_sort)

        self.graphs = [x[0] for x in graphs_and_is_cyclical]
        self.__is_cyclical = [x[1] for x in graphs_and_is_cyclical]

    def __key_graph_sort(self, x):
        return len(x[0].edges())

    def __propagate(self, i, node):
        rules_supporting_node = [x for x in self.__aba.rules if x.result == node]
        level_graph_copy = pickle.dumps(self.graphs[i], -1)
        level_history_copy = ujson.dumps(self.__history[i])
        level_is_cyclical_copy = ujson.dumps(self.__is_cyclical[i])

        for i, rule in enumerate(rules_supporting_node):
            index_used = i
            if i > 0:
                index_used = self.index_used_init(index_used, level_graph_copy, level_history_copy,
                                                  level_is_cyclical_copy)

            for symbol in rule.symbols:
                self.graphs[index_used].add_edge(node, symbol)
                if symbol is not None:
                    if symbol in self.__history[index_used]:
                        self.__is_cyclical[index_used] = True
                        break
                    self.__history[index_used].append(symbol)
                    self.__propagate(index_used, symbol)
                    self.__history[index_used].pop()

    def index_used_init(self, index_used, level_graph_copy, level_history_copy, level_is_cyclical_copy):
        self.graphs.append(pickle.loads(level_graph_copy))
        self.__history.append(ujson.loads(level_history_copy))
        self.__is_cyclical.append(ujson.loads(level_is_cyclical_copy))
        self.assumptions.append({})
        self.is_conflict_free.append(None)
        self.is_stable.append(None)
        self.__max_index += 1
        index_used = self.__max_index
        return index_used

    def __propagate_assumptions(self):
        for assumption, symbol in self.__aba.contraries.items():
            for index, graph in enumerate(self.graphs):
                if assumption in graph.nodes():
                    # `assumption` is being attacked by `symbol`
                    self.assumptions[index][assumption] = symbol

    """
    ABA definition :If attacker is in root and assumption is in root then it can not be Conflict-free"
    """

    def __is_conflict_free(self):
        for i, graph in enumerate(self.graphs):
            conflict_free = True
            for assumption, attacker in self.__aba.contraries.items():
                print("Attacker:", attacker, " attacks to", "assumption", assumption,
                      "Attacker:", attacker, "isInRoot: ", attacker in graph.nodes(),
                      ' ⧹n', "Assumption:", assumption, "isInRoot: ", assumption in graph.nodes())
                if attacker in graph.nodes() and assumption in graph.nodes():
                    conflict_free = False
                    break
            self.is_conflict_free[i] = conflict_free
            print("Root", self.root, "is conflict free: ", self.is_conflict_free[i], )

    def __is_stable(self):
        for i, graph in enumerate(self.graphs):
            stable = False
            if self.is_conflict_free[i]:
                stable = True
                for assumption, attacker in self.__aba.contraries.items():
                    if assumption not in graph.nodes():
                        if attacker not in graph.nodes():
                            stable = False
                            break

            self.is_stable[i] = stable
            print("Argument", self.root, "is stable: %s", self.is_stable[i])

    def __is_actual_argument(self, i, node):
        graph = self.graphs[i]
        if self.__is_cyclical[i]:
            return False

        neighbors = graph.successors(node)
        if len(neighbors) == 0:
            if node is None or node in self.__aba.assumptions:
                return True
            return False

        ret = True
        for neighbor in neighbors:
            ret = ret and self.__is_actual_argument(i, neighbor)
        return ret

    def is_actual_argument(self, i=0):
        return self.__is_actual_argument(i, self.root)
