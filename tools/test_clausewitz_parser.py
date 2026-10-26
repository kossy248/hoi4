"""Native source syntax must not require whitespace beside braces/operators."""
import unittest

from validate_mod import one, parse


class ClausewitzParserTests(unittest.TestCase):
    def test_adjacent_native_braces_and_equals_are_separate_tokens(self):
        self.assertEqual(parse('category={decision={cost=10}}'), [
            ('category', '=', [('decision', '=', [('cost', '=', '10')])]),
        ])

    def test_comparison_operators_remain_single_tokens(self):
        self.assertEqual(parse('a<=1 b>=2 c!=3 d=4'), [
            ('a', '<=', '1'), ('b', '>=', '2'), ('c', '!=', '3'), ('d', '=', '4'),
        ])

    def test_comments_end_at_each_supported_line_ending(self):
        for newline in ('\n', '\r\n', '\r'):
            with self.subTest(newline=repr(newline)):
                text = 'root={# ignored } {' + newline + 'child={}}'
                self.assertEqual(one(parse(text), 'root'), [('child', '=', [])])

    def test_real_unbalanced_blocks_still_fail(self):
        for text in ('root={child={}', 'root={}}'):
            with self.subTest(text=text), self.assertRaises(AssertionError):
                parse(text)


if __name__ == '__main__':
    unittest.main()
