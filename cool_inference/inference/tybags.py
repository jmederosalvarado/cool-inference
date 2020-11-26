class TyBags:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
        self.children = {}

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

    def create_child(self, key):
        child = TyBags(self)
        self.children[key] = child
        return child

    def reduce_bag(self, node, types):
        types = set(types)

        # TODO: preguntar especificamente el tipo del nodo
        try:
            var_name = node.id
        except AttributeError:
            return False

        var_types = self.find_variable(var_name)

        intersection = var_types.intersection(types)

        if len(intersection) == 0:
            self.modify_variable(var_name, set.union(var_types, types, {"@error"}))

        else:
            # TODO: revisar estos casos
            if "@error" in var_types:
                self.modify_variable(var_name, set.union(var_types, types))
            elif "@error" in types:
                self.modify_variable(var_name, types)
            else:
                self.modify_variable(var_name, intersection)

        new_var_types = self.find_variable(var_name)

        return var_types != new_var_types

    def define_variable(self, name, types):
        self.vars[name] = set(types)

    def find_variable(self, name):
        try:
            return self.vars[name]
        except KeyError:
            return self.parent and self.parent.find_variable(name)

    def modify_variable(self, name, types):
        try:
            self.vars[name] = set(types)
        except KeyError as e:
            if self.parent is not None:
                self.parent.modify_variable(name, types)
            else:
                raise e
