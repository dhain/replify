#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_replify
----------------------------------

Tests for `replify` module.
"""

import unittest
from cStringIO import StringIO

from replify import replify


class TestReplify(unittest.TestCase):
    def _helper(self, code, context=None, console_type=None):
        if context is None:
            context = {}
        infile = StringIO(code)
        outfile = StringIO()
        replify.replify(infile, outfile, context, console_type)
        return outfile.getvalue()

    def test_blank_line(self):
        input = '\n'
        result = self._helper(input)
        self.assertEqual(result, '>>> \n')
        self.assertEqual(self._helper(result), input)

    def test_blank_line_with_indent(self):
        input = '    \n'
        result = self._helper(input)
        self.assertEqual(result, '    >>> \n')
        self.assertEqual(self._helper(result), input)

    def test_one_single_line_statement(self):
        input = '1\n'
        result = self._helper(input)
        self.assertEqual(
            result,
            '>>> 1\n'
            '1\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_one_single_line_statement_with_context(self):
        input = 'a\n'
        result = self._helper(input, {'a': 1})
        self.assertEqual(
            result,
            '>>> a\n'
            '1\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_one_multi_line_statement(self):
        input = '(\n    a\n)\n'
        result = self._helper(input, {'a': 1})
        self.assertEqual(
            result,
            '>>> (\n'
            '...     a\n'
            '... )\n'
            '1\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_one_single_line_statement_with_indent(self):
        input = '    a\n'
        result = self._helper(input, {'a': 1})
        self.assertEqual(
            result,
            '    >>> a\n'
            '    1\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_inconsistent_indent_raises_ValueError(self):
        self.assertRaises(ValueError, self._helper, '    1\n2')
        self.assertRaises(ValueError, self._helper, '    >>> 1\n2')

    def test_two_single_line_statements(self):
        input = 'a\nb\n'
        result = self._helper(input, {'a': 1, 'b': 2})
        self.assertEqual(
            result,
            '>>> a\n'
            '1\n'
            '>>> b\n'
            '2\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_two_multi_line_statements(self):
        input = '(\n    a\n)\n(\n    b\n)\n'
        result = self._helper(input, {'a': 1, 'b': 2})
        self.assertEqual(
            result,
            '>>> (\n'
            '...     a\n'
            '... )\n'
            '1\n'
            '>>> (\n'
            '...     b\n'
            '... )\n'
            '2\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_def(self):
        input = 'def a():\n    b = 1\n    return b\n\na()\n'
        result = self._helper(input)
        self.assertEqual(
            result,
            '>>> def a():\n'
            '...     b = 1\n'
            '...     return b\n'
            '... \n'
            '>>> a()\n'
            '1\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_def_with_empty_line(self):
        input = (
            'def a():\n'
            '    b = 1\n'
            '    \n'
            '    return b\n'
            '\n'
            'a()\n'
        )
        result = self._helper(input)
        self.assertEqual(
            result,
            '>>> def a():\n'
            '...     b = 1\n'
            '...     \n'
            '...     return b\n'
            '... \n'
            '>>> a()\n'
            '1\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_syntaxerror(self):
        input = ')\n'
        result = self._helper(input)
        self.assertEqual(
            result,
            '>>> )\n'
            '  File "<stdin>", line 1\n'
            '    )\n'
            '    ^\n'
            'SyntaxError: invalid syntax\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_syntaxerror_inside_def(self):
        input = 'def a():\n    )\n'
        result = self._helper(input)
        self.assertEqual(
            result,
            '>>> def a():\n'
            '...     )\n'
            '  File "<stdin>", line 2\n'
            '    )\n'
            '    ^\n'
            'SyntaxError: invalid syntax\n'
        )
        self.assertEqual(self._helper(result), input)

    def test_nameerror(self):
        input = 'a\n'
        result = self._helper(input)
        self.assertEqual(
            result,
            '>>> a\n'
            'Traceback (most recent call last):\n'
            '  File "<stdin>", line 1, in <module>\n'
            "NameError: name 'a' is not defined\n"
        )
        self.assertEqual(self._helper(result), input)

    def test_nameerror_inside_call(self):
        input = (
            'def a():\n'
            '    b\n'
            '\n'
            'a()\n'
        )
        result = self._helper(input)
        self.assertEqual(
            result,
            '>>> def a():\n'
            '...     b\n'
            '... \n'
            '>>> a()\n'
            'Traceback (most recent call last):\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  File "<stdin>", line 2, in a\n'
            "NameError: global name 'b' is not defined\n"
        )
        self.assertEqual(self._helper(result), input)

    def test_import(self):
        input = 'import base64\n'
        context = {}
        result = self._helper(input, context)
        self.assertEqual(
            result,
            '>>> import base64\n'
        )
        self.assertIn('base64', context)
        self.assertEqual(self._helper(result), input)

    def test_exception_raised_by_library(self):
        input = (
            'import base64\n'
            'base64.b64decode("Z")\n'
        )
        context = {}
        result = self._helper(input, context)
        self.assertEqual(
            result,
            '>>> import base64\n'
            '>>> base64.b64decode("Z")\n'
            'Traceback (most recent call last):\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  File "{0}", line 76, in b64decode\n'
            '    raise TypeError(msg)\n'
            'TypeError: Incorrect padding\n'.format(
                context['base64'].__file__.rstrip('c'))
        )
        self.assertEqual(self._helper(result), input)

    def test_doctest_style_exception(self):
        input = (
            'import base64\n'
            'base64.b64decode("Z")\n'
        )
        context = {}
        result = self._helper(input, context, replify.DoctestTracebackConsole)
        self.assertEqual(
            result,
            '>>> import base64\n'
            '>>> base64.b64decode("Z")\n'
            'Traceback (most recent call last):\n'
            '  ...\n'
            'TypeError: Incorrect padding\n'
        )
        self.assertEqual(self._helper(result), input)


if __name__ == '__main__':
    unittest.main()
