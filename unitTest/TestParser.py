import unittest
from aba.aba_rule import ABA_Rule
from aba.aba import ABA
from aba.aba_parser import ABA_Parser
import logging


class TestParser(unittest.TestCase):
    def setUp(self):
        text = """
        assumption(xz).
        a |- b.
        c , ded |- ef.
        |- g.
        contrary(a, z).
        contrary(ded, pos).
        """
        self.parser = ABA_Parser(text)

    def test_parser_rules(self):
        self.assertEqual(self.parser.parse(), [])
        self.assertEqual(self.parser.parsed_assumptions, ['xz'])
        self.assertEqual(self.parser.parsed_rules[0], ABA_Rule(['a'], 'b'))
        self.assertEqual(self.parser.parsed_rules[1], ABA_Rule(['c', 'ded'], 'ef'))
        self.assertEqual(self.parser.parsed_rules[2], ABA_Rule([None], 'g'))
        self.assertEqual(self.parser.parsed_contraries['a'], 'z')
