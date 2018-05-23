import itertools


def concat(iterables):
    return list(itertools.chain.from_iterable(iterables))


class Node:
    pass


class Element:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Element({})".format(self.name)


class BottomElement(Element):
    def __init__(self):
        super().__init__("_")

    def __repr__(self):
        return "BottomElement()"


BOTTOM = BottomElement()


class DomainNode(Node):
    def __init__(self, name, *items):
        self.name = name
        self.items = items

    def get_graph(self):
        return [(item, BOTTOM) for item in self.items]


class OpNode(Node):
    def __init__(self, *args):
        self.args = args

    @property
    def graphs(self):
        return [arg.get_graph() for arg in self.args]


class AddNode(OpNode):
    def get_graph(self):
        return concat(self.graphs)


class MulNode(OpNode):
    def get_graph(self):
        return [
            (
                create_product_element(*[edge[0].name for edge in product_item]),
                create_product_element(*[edge[1].name for edge in product_item])
            )
            for product_item in itertools.product(*self.graphs)
        ]


def to_dot(edges):
    return "digraph G {\n" + \
           "\n".join(
               '"{}" -> "{}"'.format(v1.name, v2.name) for v1, v2 in edges
           ) +\
           "\n}"


def create_domain(name, *item_names):
    return DomainNode(name, *[Element(item_name) for item_name in item_names])


def create_product_element(*tuple_items):
    return Element("({})".format(", ".join(tuple_items)))


def main():
    A = create_domain("A", "a", "b")
    B = create_domain("B", "d", "e")
    C = create_domain("C", "f", "g")
    D = create_domain("D", "h", "k")
    # expr = MulNode(
    #     DomainNode("A"),
    #     DomainNode("B"),
    #     AddNode(DomainNode("C"), DomainNode("D"))
    # )
    # edges = AddNode(DomainNode("A", Element("a"), Element("b")), DomainNode("B", Element("c"), Element("d"))).get_graph()
    edges = MulNode(A, B, AddNode(C, D)).get_graph()
    print(to_dot(edges))


if __name__ == "__main__":
    main()
