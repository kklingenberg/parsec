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


atom = errormessage("input is neither a valid number "\
                        "nor a valid variable name")(or_(number, variable))


#: (literal, precedence) 0 is maximum precedence
infix_operations = dict([
    ('+', 3),
    ('*', 2),
    ('-', 3),
    ('/', 2),
    ('^', 1)])

prefix_operations = [
    pmap(literal('-'))(lambda _: Operation("negate")),
    pmap(literal('sin'))(Operation),
    pmap(literal('cos'))(Operation)]


spaces = many(space)


def expression(string):
    value, remainder = sequence(
        spaces,
        or_(prefix_expression, wrapped_expression, atom),
        spaces,
        try_(infix_expression),
        spaces)(string)
    _, exp, _, infix, _ = value
    if infix is None:
        return (exp, remainder)
    return ([infix[0],  # the operation
             exp,       # the left-side argument
             infix[1]], # the right-side argument
            remainder)


@pmap(sequence(literal('('), expression, literal(')')))
def wrapped_expression(value):
    return value[1]


@pmap(sequence(or_(*prefix_operations), spaces, or_(wrapped_expression, atom)))
def prefix_expression(value):
    return [value[0], value[2]]


def infix_expression(string):
    op, remainder = or_(*map(literal, infix_operations))(string)
    precedence = infix_operations[op]
    # TODO handle precedence
    exp, remainder = expression(remainder)
    return ([Operation(op), exp], remainder)
