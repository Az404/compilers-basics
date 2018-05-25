import re
import operator
import sys
import os


OPERATIONS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv
}


class NumExpr:
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "({})".format(" ".join(str(arg) for arg in self.args))


class ParsingError(Exception):
    pass


def parse_expression(expression):
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
            if len(args) != 2:
                raise ParsingError(
                    "Expected 2 arguments, found {}: {}".format(len(args), args))
            converted_args = [
                int(arg) if isinstance(arg, str) else arg
                for arg in args
            ]
            stack[-1].append(NumExpr(op, *converted_args))
        else:
            stack[-1].append(token)
    return stack.pop()[0]


class Transformer:
    def __init__(self):
        self.transitions = []

    def step(self, tree: NumExpr):
        op, rand1, rand2 = tree.args
        result = None

        if isinstance(rand1, NumExpr):
            result = NumExpr(op, self.step(rand1), rand2)

        if isinstance(rand1, int) and isinstance(rand2, NumExpr):
            result = NumExpr(op, rand1, self.step(rand2))

        if isinstance(rand1, int) and isinstance(rand2, int):
            result = calculate(op, rand1, rand2)

        self.transitions.append((tree, result))
        return result


def calculate(op, rand1, rand2):
    return OPERATIONS[op](rand1, rand2)


def make_steps(expression):
    result = []
    while isinstance(expression, NumExpr):
        transformer = Transformer()
        expression = transformer.step(expression)
        result.append(transformer.transitions)
    return result


def main():
    if len(sys.argv) < 2:
        filename = os.path.basename(__file__)
        print("Usage: python3 {} <expression>".format(filename))
        print('Example: python3 {} "(/ 100 (* (- 7 4) (+ 5 6)))"'.format(
            filename))
        return
    expression = sys.argv[1]
    try:
        tree = parse_expression(expression)
        if not isinstance(tree, NumExpr) and not isinstance(tree, int):
            raise Exception
    except Exception as e:
        error = str(e) if isinstance(e, ParsingError) else\
            "Expression parsing failed."
        print(error)
        return
    for index, step in enumerate(make_steps(tree)):
        print("Step {}:".format(index + 1))
        for transition in step:
            print("\t{} => {}".format(*transition))
            if transition != step[-1]:
                print("\t" + "-"*75)


if __name__ == "__main__":
    main()
