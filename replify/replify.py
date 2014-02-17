#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import code
import traceback
import argparse

ps1 = '>>> '
ps2 = '... '


class Indentifier(object):
    def __init__(self, outfile, initial_indent):
        self.outfile = outfile
        self.initial_indent = initial_indent
        self.last_char = '\n'

    def write(self, data):
        if self.last_char == '\n' and data:
            self.outfile.write('{0}{1}'.format(self.initial_indent, data))
        else:
            self.outfile.write(data)
        if data:
            self.last_char = data[-1]

    def flush(self):
        self.outfile.flush()

    def close(self):
        self.outfile.close()


class DoctestTracebackConsole(code.InteractiveConsole):
    def showtraceback(self):
        lines = ['Traceback (most recent call last):\n', '  ...\n']
        try:
            type, value, tb = sys.exc_info()
            lines.extend(traceback.format_exception_only(type, value))
        finally:
            tb = None           # noqa
        for line in lines:
            self.write(line)


def replify(infile, outfile, context, console_type=None):
    if console_type is None:
        console_type = code.InteractiveConsole
    console = console_type(context, '<stdin>')
    dereplify = False
    initial_indent = None
    needmore = False
    _stdout = sys.stdout
    _stderr = sys.stderr
    sys.stdout = sys.stderr = outfile
    try:
        for line in infile:
            if initial_indent is None:
                initial_indent = re.match(
                    r'\s*', line.rstrip('\r\n')).group(0)
                sys.stdout = sys.stderr = Indentifier(outfile, initial_indent)
                if line.lstrip().startswith(ps1):
                    dereplify = True
            if line.startswith(initial_indent):
                line = line[len(initial_indent):]
            else:
                raise ValueError()
            if dereplify:
                if line.startswith(ps1):
                    line = line[len(ps1):]
                elif line.startswith(ps2):
                    line = line[len(ps2):]
                else:
                    line = ''
                sys.stdout.write(line)
            else:
                sys.stdout.write(
                    '{0}{1}'.format(ps2 if needmore else ps1, line))
                needmore = console.push(line.rstrip('\r\n'))
    finally:
        sys.stdout = _stdout
        sys.stderr = _stderr


def main():
    parser = argparse.ArgumentParser(
        description='Adds or removes ">>>" prompt prefix from input lines.'
    )
    parser.add_argument(
        'context_module', metavar='MODULE', nargs='?',
        help='Path to python module to execute as context.')
    parser.add_argument(
        '-i', '--infile', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument(
        '-o', '--outfile', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument(
        '-d', '--doctest-tb', dest='console_type', action='store_const',
        const=DoctestTracebackConsole, default=code.InteractiveConsole,
        help='Output doctest-style tracebacks.')

    config = parser.parse_args()

    context = {}
    if config.context_module:
        exec(compile(
            open(config.context_module, 'rb').read(),
            config.context_module, 'exec'
        ), context)

    replify(config.infile, config.outfile, context, config.console_type)

    sys.exit(0)


if __name__ == '__main__':
    main()
