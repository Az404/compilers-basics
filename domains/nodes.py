import itertools

from utils import normalize_relations, concat

BOTTOM = "_"


class Node:
    pass


class DomainNode(Node):
    def __init__(self, domain_name, *items, relations=None):
        relations = relations or []
        self.name = domain_name
        self.items = list(set(list(items) + concat(relations)))
        self.relations = normalize_relations((relations) + [
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
