import itertools

BOTTOM = "_"


def concat(iterables):
    return list(itertools.chain.from_iterable(iterables))


def normalize_relations(relations):
    items = list(set(concat(relations)))
    item_index = {item: index for index, item in enumerate(items)}
    matrix = [[None for _ in range(len(items))] for _ in range(len(items))]
    for relation in relations:
        matrix[item_index[relation[0]]][item_index[relation[1]]] = 1

    for i in range(len(items)):
        matrix[i][i] = 0

    for i in range(len(items)):
        for j in range(len(items)):
            for k in range(len(items)):
                if not matrix[i][k] or not matrix[k][j]:
                    continue
                matrix[i][j] = max(matrix[i][j] or 0, matrix[i][k] + matrix[k][j])

    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if matrix[i][j] == 1:
                result.append((items[i], items[j]))
        result.append((items[i], items[i]))
    return result


class Node:
    pass


class DomainNode(Node):
    def __init__(self, domain_name, *items, relations=None):
        self.name = domain_name
        self.items = items
        self.relations = normalize_relations((relations or []) + [
            (BOTTOM, item) for item in self.items
        ])

    def get_relations(self):
        return self.relations


class OpNode(Node):
    def __init__(self, *args):
        self.args = args
        self.name = self.op_name + "_".join(arg.name for arg in args)

    @property
    def arg_relations(self):
        return [arg.get_relations() for arg in self.args]

    @property
    def op_name(self):
        pass


class AddNode(OpNode):
    @property
    def op_name(self):
        return "+"

    def get_relations(self):
        return concat([
            [
                self._bind_domain(arg, relation)
                for relation in arg.get_relations()
            ]
            for arg in self.args
        ])

    def _bind_domain(self, domain, relation):
        def item_bind(item):
            if item == BOTTOM:
                return item
            return (domain.name, item)

        return item_bind(relation[0]), item_bind(relation[1])


class MulNode(OpNode):
    @property
    def op_name(self):
        return "*"

    def get_relations(self):
        def make_composite(items):
            if all(item == BOTTOM for item in items):
                return BOTTOM
            return tuple(items)

        relations = []
        for product_item in itertools.product(*self.arg_relations):
            relations.append((
                make_composite([edge[0] for edge in product_item]),
                make_composite([edge[1] for edge in product_item])
            ))
        return normalize_relations(relations)


def to_dot(edges):
    return "digraph G {\n" + \
           "\n".join(
               '"{}" -> "{}"'.format(to_string(v2), to_string(v1)) for v1, v2 in
               edges if v1 != v2
           ) + \
           "\n}"


def to_string(item):
    if isinstance(item, tuple):
        return "({})".format(", ".join([to_string(x) for x in item]))
    return str(item)


def main():
    A = DomainNode("A", "a", "b", "d", relations=[("a", "b"), ("b", "c"), ("d", "c")])
    B = DomainNode("B", "d", "e")
    C = DomainNode("C", "f", "h")
    D = DomainNode("D", "k", "l")
    edges = MulNode(A, B).get_relations()
    print(to_dot(edges))


if __name__ == "__main__":
    main()
