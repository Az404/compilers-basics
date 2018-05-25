import re
import sys
import os

from nodes import Node, AddNode, MulNode
from utils import to_dot
import domains

OPERATIONS = {
    "+": AddNode,
    "*": MulNode
}


class ParsingError(Exception):
    pass


def parse_expression(expression, symbols):
    stack = [[]]
    for token in re.split("(\s|\(|\))", expression):
        if not token.strip():
            continue
        if token == "(":
            stack.append([])

        elif token == ")":
            op, *args = stack.pop()
            if op not in OPERATIONS:
                raise ParsingError("Unsupported operation: {}".format(op))
            bad_domains = [arg for arg in args if not isinstance(arg, Node)]
            if bad_domains:
                raise ParsingError("No such domains: {}".format(bad_domains))
            stack[-1].append(OPERATIONS[op](*args))

        else:
            stack[-1].append(symbols[token] if token in symbols else token)

    if not isinstance(stack[-1][0], Node):
        raise ParsingError("Expression parsing failed.")
    return stack[-1][0]


def main():
    if len(sys.argv) < 2:
        filename = os.path.basename(__file__)
        print("Usage: python3 {} <expression>".format(filename))
        print('Example: python3 {} "(* A B (+ C D))"'.format(filename))
        return
    try:
        tree = parse_expression(sys.argv[1], vars(domains))
    except Exception as e:
        error = str(e) if isinstance(e, ParsingError) else \
            "Expression parsing failed."
        print(error)
        return

    edges = tree.get_relations()
    print(to_dot(edges))


if __name__ == "__main__":
    main()
