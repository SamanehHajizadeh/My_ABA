import unittest

from aba.aba_framework import ABA_framework
from aba.rulegenerator import RuleGenerator


class TwoSymbolsTest(unittest.TestCase):
    def setUp(self):
        self.aba = ABA_framework()
        self.aba.symbols = ('a', 'b')
        self.aba.rules.append(RuleGenerator(['a'], 'b'))
        self.aba.rules.append(RuleGenerator(['b'], 'a'))

        self.aba.extract_assumptions_from_contraries()

    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.generates_instances_of_Dispute_Tree_and_append_to_dispute_trees()

        self.assertEqual(self.aba.arguments, [])
