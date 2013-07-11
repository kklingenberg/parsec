"""
Parser functions and combinators.

A parser is a procedure that takes a string as input, and returns a
value and the remainder of the string that wasn't consumed, or raises
an Exception.
"""

import functools


class ParseError(Exception): pass


def many(p):
    """Returns a parser that attempts the parser *p* at least zero
    times. It consumes as much as possible, and returns a list of
    results. The resulting parser cannot fail with a ParseError."""
    def parser(string):
        result = []
        while True:
            try:
                value, remainder = p(string)
                if remainder == string:
                    raise ParseError("no input is being consumed")
                result.append(value)
                string = remainder
            except ParseError:
                return (result, string)
    return parser


def manyone(p):
    """Returns a parser that attempts the parser *p* at least one
    time. It consumes as much as possible, and returns a list of
    results."""
    def parser(string):
        value, remainder = p(string)
        values, remainder = many(p)(remainder)
        return ([value] + values, remainder)
    return parser


def sequence(*ps):
    """Makes a parser that sequences others, accumulating the results
    in a list."""
    def parser(string):
        result = []
        for p in ps:
            val, string = p(string)
            result.append(val)
        return (result, string)
    return parser


def concat(*ps):
    """Sequences parsers that return strings and concatenates the
    result, filtering out ``None``."""
    def parser(string):
        values, remainder = sequence(*ps)(string)
        if values is None:
            return (None, remainder)
        return ("".join(filter(bool, values)), remainder)
    return parser


def pmap(p):
    """Maps a function to the result of parser *p*. Returns a parser."""
    def wrapper(function):
        @functools.wraps(function)
        def parser(string):
            value, remainder = p(string)
            return (function(value), remainder)
        return parser
    return wrapper


def or_(*ps):
    """Returns a parser that attempts the given parsers in order, and
    returns the result of the first one that doesn't fail. If all
    fail, then the parser fails."""
    def parser(string):
        for p in ps:
            try:
                val, remainder = p(string)
                return (val, remainder)
            except ParseError:
                pass
        raise ParseError("none of the given parsers apply")
    return parser


def try_(p):
    """Returns a parser that attempts to execute the given parser, but
    doesn't fail if the given parser fails, it just returns ``None``
    and doesn't consume input."""
    def parser(string):
        try:
            val, remainder = p(string)
            return (val, remainder)
        except ParseError:
            return (None, string)
    return parser


def digit(string):
    if not string:
        raise ParseError("empty string")
    code = ord(string[0])
    if code <= 57 and code >= 48:
        return (string[0], string[1:])
    raise ParseError("not a digit")


def letter(string):
    """ASCII letter, just for ease of implementation."""
    if not string:
        raise ParseError("empty string")
    code = ord(string[0])
    if (code <= 90 and code >= 65) or (code <= 122 and code >= 97):
        return (string[0], string[1:])
    raise ParseError("not a letter")


def literal(lit):
    """Matches a literal substring."""
    if not lit:
        raise ValueError("literal mustn't be an empty string")
    def parser(string):
        if string.startswith(lit):
            return (lit, string[len(lit):])
        raise ParseError("doesn't match literal '%s'" % lit)
    return parser


def end(string):
    """Matches the end of input."""
    if string:
        raise ParseError("not the end of input")
    return (None, "")
