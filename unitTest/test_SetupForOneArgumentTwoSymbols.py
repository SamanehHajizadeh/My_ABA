import unittest

from aba.assumptionBaseArg_framework import AbaFramework
from aba.rulegenerator import RuleGenerator


class test_OneArgumentTwoSymbols(unittest.TestCase):

    def setUp(self):
        self.aba = AbaFramework()
        self.aba.symbols = ('a', 'b', 'c')
        self.aba.rules.append(RuleGenerator(['a'], 'b'))
        self.aba.rules.append(RuleGenerator(['b'], 'a'))
        self.aba.rules.append(RuleGenerator([None], 'c'))

        for r in self.aba.rules:
            print(r)

        self.aba.extract_assumptions_from_contraries()
