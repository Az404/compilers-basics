import itertools


def concat(iterables):
    return list(itertools.chain.from_iterable(iterables))


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


def normalize_relations(relations):
    """
    Makes reflexive-transitive closure.
    :param relations
    :return: covering and reflexive relations only
    """
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
