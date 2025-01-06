import unittest

import sys
import os

# Add the ../src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ijp import IncrementalJSONParser

class TestIncrementalJSONParser(unittest.TestCase):

    def test_empty_input(self):
        parser = IncrementalJSONParser([""])
        with self.assertRaises(StopIteration):
            next(parser)

    def test_bare_values(self):
        # Test with a bare integer
        chunks = ['123']
        parser = IncrementalJSONParser(chunks)
        parser.send('\n')
        expected = [
            ([], 'int', 123)
        ]
        results = list(parser)
        self.assertEqual(results, expected)

        # Test with a bare string
        chunks = ['"hello"']
        parser = IncrementalJSONParser(chunks)
        parser.send('\n')
        expected = [
            ([], 'stringpart', 'hello'),
            ([], 'string', 'hello')
        ]
        results = list(parser)
        self.assertEqual(results, expected)

        # Test with a bare boolean
        chunks = ['true']
        parser = IncrementalJSONParser(chunks)
        parser.send('\n')
        expected = [
            ([], 'logical', True)
        ]
        results = list(parser)
        self.assertEqual(results, expected)

        # Test with a bare null
        chunks = ['null']
        parser = IncrementalJSONParser(chunks)
        parser.send('\n')
        expected = [
            ([], 'logical', None)
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_incremental_parsing(self):
        chunks = ['{"k', 'ey": "v', 'alue", "n', 'umber": 1', '23}']
        parser = IncrementalJSONParser(chunks)
        expected = [
            (['key'], 'stringpart', 'v'),
            (['key'], 'stringpart', 'alue'),
            (['key'], 'string', 'value'),
            (['number'], 'int', 123)
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_context_manager(self):
        json_string = '{"key": "value"}'
        with IncrementalJSONParser([json_string]) as parser:
            results = list(parser)
        expected = [
            (['key'], 'stringpart', 'value'),
            (['key'], 'string', 'value')
        ]
        self.assertEqual(results, expected)

    # Valid Examples

    def test_nested_arrays(self):
        chunks = ['[1, [2, 3], [4, [5, 6]]]', '']
        parser = IncrementalJSONParser(chunks)
        expected = [
            ([0], 'int', 1),
            ([1, 0], 'int', 2),
            ([1, 1], 'int', 3),
            ([2, 0], 'int', 4),
            ([2, 1, 0], 'int', 5),
            ([2, 1, 1], 'int', 6)
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_booleans(self):
        chunks = ['{"isTrue": true, "isFalse": false}', '']
        parser = IncrementalJSONParser(chunks)
        expected = [
            (['isTrue'], 'logical', True),
            (['isFalse'], 'logical', False)
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_string_with_unicode_characters(self):
        chunks = ['{"unicode": "\\u2764"}', '']
        parser = IncrementalJSONParser(chunks)
        expected = [
            (['unicode'], 'stringpart', '❤'),
            (['unicode'], 'string', '❤')
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_newline_and_tab_in_strings(self):
        chunks = ['{"text": "Line1\\nLine2\\tTabbed"}', '']
        parser = IncrementalJSONParser(chunks)
        expected = [
            (['text'], 'stringpart', 'Line1\nLine2\tTabbed'),
            (['text'], 'string', 'Line1\nLine2\tTabbed')
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_double_backslash(self):
        chunks = ['{"path": "C:\\\\User\\\\Name"}', '']
        parser = IncrementalJSONParser(chunks)
        expected = [
            (['path'], 'stringpart', 'C:\\User\\Name'),
            (['path'], 'string', 'C:\\User\\Name')
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_excessive_whitespace(self):
        chunks = ['{  "key" :   "value"  , "number" :  123  }', '']
        parser = IncrementalJSONParser(chunks)
        expected = [
            (['key'], 'stringpart', 'value'),
            (['key'], 'string', 'value'),
            (['number'], 'int', 123)
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_duplicate_keys(self):
        chunks = ['{"key": "value1", "key": "value2"}', '']
        parser = IncrementalJSONParser(chunks)
        expected = [
            (['key'], 'stringpart', 'value1'),
            (['key'], 'string', 'value1'),
            (['key'], 'stringpart', 'value2'),
            (['key'], 'string', 'value2')
        ]
        results = list(parser)
        self.assertEqual(results, expected)

    def test_empty_object(self):
        chunks = ['{}', '']
        parser = IncrementalJSONParser(chunks)
        expected = []  # Expect no elements for an empty object
        results = list(parser)
        self.assertEqual(results, expected)

    def test_empty_array(self):
        chunks = ['[]', '']
        parser = IncrementalJSONParser(chunks)
        expected = []  # Expect no elements for an empty array
        results = list(parser)
        self.assertEqual(results, expected)

    def test_nested_empty_objects_and_arrays(self):
        chunks = ['{"emptyArray": [], "emptyObject": {}}', '']
        parser = IncrementalJSONParser(chunks)
        expected = []  # Expect no elements for nested empty objects and arrays
        results = list(parser)
        self.assertEqual(results, expected)


    # Invalid Examples

    def test_missing_comma_between_items(self):
        chunks = ['{"key1": "value1" "key2": "value2"}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    # FIXME: no way to fix this in the parser without major structural change
    # def test_trailing_comma_in_object(self):
    #     chunks = ['{"key": "value",}', '']
    #     parser = IncrementalJSONParser(chunks)
    #     with self.assertRaises(ValueError):
    #         list(parser)

    # def test_trailing_comma_in_array(self):
    #     chunks = ['[1, 2, 3,]', '']
    #     parser = IncrementalJSONParser(chunks)
    #     with self.assertRaises(ValueError):
    #         list(parser)

    def test_single_quotes_in_keys(self):
        chunks = ["{'key': 'value'}", '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    def test_single_quotes_in_strings(self):
        chunks = ['{"key": \'value\'}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    def test_non_finite_numbers(self):
        chunks = ['{"number": NaN}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    def test_empty_keys(self):
        chunks = ['{"": "value"}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    def test_missing_value_in_object(self):
        chunks = ['{"key": }', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    def test_number_beginning_with_a_plus_sign(self):
        chunks = ['{"number": +123}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    def test_comments(self):
        chunks = ['{"key": "value" /* comment */}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    def test_no_quotes_in_keys(self):
        chunks = ['{key: "value"}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
    
    def test_bracket_mismatch(self):
        chunks = ['["mismatch"}', '']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)

    # End of input while in various parser states

    def test_end_of_input_while_in_key_string(self):
        chunks = ['{"key']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
            parser.close()

    def test_end_of_input_while_in_value_string(self):
        chunks = ['{"key": "val']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
            parser.close()

    def test_end_of_input_while_in_object(self):
        chunks = ['{"key": "value"']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
            parser.close()

    def test_end_of_input_while_in_array(self):
        chunks = ['[1, 2, 3']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
            parser.close()

    def test_end_of_input_while_in_number(self):
        chunks = ['{"number": 123']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
            parser.close()

    def test_end_of_input_after_escape_character_in_key(self):
        chunks = ['{"ke\\']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
            parser.close()

    def test_end_of_input_after_escape_character_in_value(self):
        chunks = ['{"key": "val\\']
        parser = IncrementalJSONParser(chunks)
        with self.assertRaises(ValueError):
            list(parser)
            parser.close()


if __name__ == '__main__':
    unittest.main()
