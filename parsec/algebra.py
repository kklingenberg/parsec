"""
Parser for algebraic expressions.
"""

from parsec.parse import *


class Symbol(object):

    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.symbol)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("can't compare {0} with {1}".\
                                format(self.__class__, other.__class__))
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)


class Variable(Symbol): pass
class Operation(Symbol): pass


@errormessage("input is not a valid number")
@pmap(sequence(manyone(digit), try_(sequence(literal('.'), manyone(digit)))))
def number(value):
    """All numbers are considered real numbers and stored as
    floats."""
    intdigits, floatpart = value
    if floatpart is None:
        return float("".join(intdigits))
    dot, decimaldigits = floatpart
    return float("".join(intdigits + [dot] + decimaldigits))


@errormessage("input is not a valid variable name")
@pmap(sequence(letter, many(or_(letter, digit, literal('_')))))
def variable(value):
    """A variable starts with a letter and is followed by numbers,
    letters or '_'."""
    first, rest = value
    return Variable("".join([first] + rest))


#: enum to describe operations
INFIX = 0
PREFIX = 1
BOTH = 2

#: (parser, type)
operations = [
    (literal('*'), INFIX),
    (literal('+'), PREFIX),
    (literal('-'), BOTH),
    (literal('/'), INFIX),
    (literal('^'), INFIX),
    (literal('sin'), PREFIX),
    (literal('cos'), PREFIX)]

def make_operations(table):
    """Builds the parser that correctly interprets an operation
    defined in *table*."""
    pass
