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
@pmap(sequence(try_(literal('-')),
               dropvalue(many(space)),
               manyone(digit),
               try_(sequence(literal('.'), manyone(digit)))))
def number(value):
    """All numbers are considered real numbers and stored as
    floats."""
    dash, _, intdigits, floatpart = value
    sign = -1
    if dash is None:
        sign = 1
    if floatpart is None:
        return sign * float("".join(intdigits))
    dot, decimaldigits = floatpart
    return sign * float("".join(intdigits + [dot] + decimaldigits))


@errormessage("input is not a valid variable name")
@pmap(sequence(letter, many(or_(letter, digit, literal('_')))))
def variable(value):
    """A variable starts with a letter and is followed by numbers,
    letters or '_'."""
    first, rest = value
    return Variable("".join([first] + rest))


#: (literal, precedence)
infix_operations = dict([
    ('+', 1),
    ('*', 2),
    ('-', 1),
    ('/', 2),
    ('^', 3)])

def minprecedence():
    return min(infix_operations.itervalues())

prefix_operations = [
    pmap(literal('-'))(lambda _: Operation("negate")),
    pmap(literal('sin'))(Operation),
    pmap(literal('cos'))(Operation)]


spaces = many(space)


def expression(current_precedence):
    def parser(string):
        value, remainder = sequence(
            spaces,
            or_(number, prefix_expression, wrapped_expression, variable),
            spaces,
            many(infix_expression(current_precedence)),
            spaces)(string)
        _, exp, _, infixes, _ = value
        for infix in infixes:
            # operation, left-hand side, right-hand side
            exp = [infix[0], exp, infix[1]]
        return (exp, remainder)
    return parser


def full_expression(string):
    """A complete algebraic expression, including precedence
    consideration."""
    parser = expression(minprecedence())
    return parser(string)


@pmap(sequence(literal('('), full_expression, literal(')')))
def wrapped_expression(value):
    return value[1]


def prefix_expression(string):
    parser = sequence(
        or_(*prefix_operations),
        spaces,
        or_(wrapped_expression, number, prefix_expression, variable))
    value, remainder = parser(string)
    return ([value[0], value[2]], remainder)


def infix_expression(current_precedence):
    """Starting with the infix operation. The left hand side argument
    has already been parsed."""
    def parser(string):
        op, remainder = or_(*map(literal, infix_operations))(string)
        precedence = infix_operations[op]
        if precedence < current_precedence:
            raise ParseError("")
        exp, remainder = expression(precedence)(remainder)
        return ([Operation(op), exp], remainder)
    return parser


def parse_expression(input_):
    return runparser(full_expression, input_)
