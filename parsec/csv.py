"""
A CSV parser.
"""

from parsec.parse import *


@pmap(or_(sequence(literal('"'), many(except_('"', '\n')), literal('"')),
          sequence(return_(None), many(except_(',', ';', '\n')), return_(None))))
def value(val):
    """A single value or cell."""
    _, content, _ = val
    return "".join(content)


@pmap(sequence(many(sequence(value, literal(','))),
               value,
               or_(literal(';\n'), literal(';'), literal('\n'), end)))
def line(val):
    """A line of comma-separated values, ending in ';', end of line,
    or both."""
    butlast, last, _ = val
    values = [val[0] for val in butlast]
    values.append(last)
    return values


@pmap(many(line))
def lines(vals):
    """An array of lines of comma-separated values."""
    return vals


def parse_csv(string):
    return runparser(lines, string)
