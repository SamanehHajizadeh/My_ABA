import unittest
from aba.aba_rule import ABA_Rule
from aba.aba import ABA
from aba.aba_parser import ABA_Parser
import logging


class TwoSymbolsTest(unittest.TestCase):
    def setUp(self):

        self.aba = ABA()
        self.aba.symbols = ('a', 'b')
        self.aba.rules.append(ABA_Rule(['a'], 'b'))
        self.aba.rules.append(ABA_Rule(['b'], 'a'))

        self.aba.extract_assumptions_from_contraries()

    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.generates_instances_of_Dispute_Tree_and_append_to_dispute_trees()

        self.assertEqual(self.aba.arguments, [])
