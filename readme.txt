# Assumption-based Argumentation(ABA) consists of (L, R, A, -)
# "L" is sentences (R + A)
# "R" stands for rules (ABA_Rules)
# "A" is assumptions A<H,h>
# "-" is contrary set, mapped from Assumption to Language that (assumptions attacks another one)
#
# MAIN CLASS --> ABA()
# arguments : list <ABA_graph>
# assumptions: list<String>
# dispute_trees : list<ABA_Dispute_Tree>
# nonAssumptions: list<String>
# potential_arguments : list<ABA_Graph>
#
# symbols : list<String>
# rules: list<ABA_Rule>
# contraries : dict(String, string) // value in symbols that attach it's assumption //KEY is an assumption.
#
#
# Methods:
#
# is_all_assumption_have_contrary(self):
# #Each assumption must have a contrary.
#
# extract_assumptions_from_contraries():
# #infer_assumptions to extract the assumptions from the contraries
#
# construct_arguments():
# #To construct the argument trees
# #Check if all assumptions have its contrary
# #It append instances of ABA_Graph objects to “potential_arguments” and appended to “arguments” if satisfy criteria being an actual argument
#
# CLASS --> ABA_Rule()
# “symbols”: a list representing the symbols supporting the result of this rule
# “result” : a string representing the result or claim or conclusion of this rule
#
# If “symbols” is an empty list => the rule represents a ground truth.
#
# Methods:
# “is_ground_truth” : returns a Boolean, if  rule is a ground truth or not.
#
# class -> ABA_Graph()
# represents arguments of the same claim symbol in ABA.
#
# requires an ABA object and a string representing argument claim symbol,in which the argument tree is to be constructed.
# The class constructor will call the construction of the argument trees, extraction of assumption set of each argument, and conflict-free and stable semantics computation for each argument.
# This class contains the following public properties, which are available for usage after the class has been instantiated:
#
# "root" : root of the argument trees.
# “graphs”: a list of Networkx DiGraph objects. each object representing an argument with the same root symbol.
# “assumptions”, : A list of list containing the assumption set for each argument.
# “is_conflict_free”: a list show if the argument (of given index) are conflict-free semantics.
# “is_stable” : a list show if the argument (of given index) are stable.
#
# method:
#  “is_actual_argument” : if the argument (of a given index) is an actual argument.
#
# class -> ABA_Dispute_Tree()
# represents dispute tree of each argument in ABA, from one ABA_Graph.
# It needs to compute the grounded and admissible semantics.
#
# “graphs”, a list of Networkx’s DiGraph objects, representing the dispute trees with the same argument root.
# “root_arg”, an ABA_Graph object, representing the argument at the root of dispute tree.
# “arg_index”, an integer, representing the argument tree’s index at the ABA_Graph object. Since an ABA_Graph object might have more than one argument, it is required to have a tracking integer to point which argument that is currently being used for constructing the dispute tree.
# “is_grounded”, a list representing whether the dispute tree (of given index) satisfies grounded semantics.
# “is_admissible”, a list representing whether the dispute tree (of given index) satisfies admissible semantics.
# “is_complete”, a list representing whether the dispute tree (of given index) satisfies ideal semantics. This property is externally computed at ABA class because it needs to know other dispute trees admissible semantics.
# “is_ideal”, a list representing whether the dispute tree (of given index) satisfies ideal semantics. This property is externally computed at ABA class because it needs to know other dispute trees admissible semantics.
#
# Methods:
#
# simulating the attacks between the proponent nodes and opponent nodes.