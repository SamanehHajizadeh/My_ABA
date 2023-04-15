import unittest
from aba.aba_rule import ABA_Rule
from aba.aba import ABA


class MultipleDisputeTrees(unittest.TestCase):
    def setUp(self):
        print("start")

    def test_1(self):
        """
        a1 |- c.
        a2 |- c.
        b1 |- d.
        b2 |- d.
        contrary(a1, d).
        contrary(a2, d).
        contrary(b1, c).
        contrary(b2, c).
        """

        aba = ABA()
        aba.symbols = ('a1', 'a2', 'b1', 'b2', 'c', 'd')
        aba.rules.append(ABA_Rule(['a1'], 'c'))
        aba.rules.append(ABA_Rule(['a2'], 'c'))
        aba.rules.append(ABA_Rule(['b1'], 'd'))
        aba.rules.append(ABA_Rule(['b2'], 'd'))
        aba.contraries['a1'] = 'd'
        aba.contraries['a2'] = 'd'
        aba.contraries['b1'] = 'c'
        aba.contraries['b2'] = 'c'

        aba.extract_assumptions_from_contraries()
        aba.construct_arguments()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['a1', 'a2', 'b1', 'b2', 'c', 'c', 'd', 'd'])

        aba.generates_instances_of_Dispute_Tree_and_append_to_dispute_trees()
