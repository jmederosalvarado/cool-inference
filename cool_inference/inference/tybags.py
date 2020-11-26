class TyBags:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
        self.children = {}
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.vars)

    def __str__(self):
        output = ""

        for key, value in self.vars.items():
            output += "\t" + str(key) + ":" + str(value) + "\n"
        for key, chil in self.children.items():
            output += "\n"
            try:
                output += key.id + "--->"
            except AttributeError:
                output += "let or case --->"
            output += "\n"
            output += str(chil)
        return output

    def __repr__(self):
        return str(self)

    # key tiene tipo node, esto lo hago para definir en la primera pasada
    # un ambiente de bolsas de tipo nuevo para cada método, let, etc, durante
    # la primera pasada. Y para poder acceder al que le corresponde a cada
    # uno durante la segunda pasada.
    def create_child(self, key):
        child = TyBags(self)
        self.children[key] = child
        return child

    def reduce_bag(self, node, types):
        types = set(types)

        try:
            var_name = node.id
        except AttributeError:
            return False

        var_types = self.find_variable(var_name)

        inters = var_types & types

        if len(inters) == 0:
            if "@error" not in var_types and "@error" not in types:
                self.modify_variable(var_name, set.union(var_types, types) + ["@error"])
            else:
                self.modify_variable(var_name, set.union(var_types, types))

        else:
            if "@error" in var_types:
                self.modify_variable(var_name, set.union(var_types, types))
            elif "@error" in types:
                self.modify_variable(var_name, types)
            else:
                self.modify_variable(var_name, inters)

        new_var_types = self.find_variable(var_name)

        return not sorted(var_types) == sorted(new_var_types)

    def define_variable(self, name, types):
        self.vars[name] = set(types)

    def find_variable(self, name):
        try:
            return self.vars[name]
        except KeyError:
            if self.parent is not None:
                return self.parent.find_variable(name)
            else:
                return None

    def modify_variable(self, name, types):
        try:
            _ = self.vars[name]
            self.vars[name] = types
        except KeyError:
            if self.parent is not None:
                self.parent.modify_variable(name, types)
            else:
                None
