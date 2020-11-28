# TODO: esto esta maja
def lowest_common_ancestor(type_1, type_2, context):
    object_type = context.get_type("Object")
    if type_1 == object_type or type_2 == object_type:
        return object_type

    typex = type_1
    while typex is not None and typex != object_type:
        if type_2.conforms_to(typex):
            return typex
        typex = typex.parent

    typex = type_2
    while typex is not None and typex != object_type:
        if type_1.conforms_to(typex):
            return typex
        typex = typex.parent

    return object_type


def solve_bag(bag, context):
    result = context.get_type(list(bag)[0])
    for ty in bag:
        ty = context.get_type(ty)
        result = lowest_common_ancestor(result, ty, context)
    return result.name
