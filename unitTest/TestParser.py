import unittest

from aba.argumet_transformer import Argumet_transformer
from aba.rulegenerator import RuleGenerator


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
        self.parser = Argumet_transformer(text)

    def test_parser_rules(self):
        self.assertEqual(self.parser.parse(), [])
        self.assertEqual(self.parser.parsed_assumptions, ['xz'])
        self.assertEqual(self.parser.parsed_rules[0], RuleGenerator(['a'], 'b'))
        self.assertEqual(self.parser.parsed_rules[1], RuleGenerator(['c', 'ded'], 'ef'))
        self.assertEqual(self.parser.parsed_rules[2], RuleGenerator([None], 'g'))
        self.assertEqual(self.parser.parsed_contraries['a'], 'z')
