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
                output += "let or case--->"
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
                self.modify_variable(
                    var_name, set.union(set.union(var_types, types), set(["@error"]))
                )

            else:
                self.modify_variable(var_name, set.union(var_types, types))

        else:
            if "@error" in var_types:
                self.modify_variable(var_name, set.union(var_types, types))
                print((var_name, self.find_variable(var_name)))
            elif "@error" in types:
                self.modify_variable(var_name, types)
            else:
                self.modify_variable(var_name, inters)

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

    def clean(self):
        for _, value in self.vars.items():
            if "@error" in value:
                value.remove("@error")
        for _, chil in self.children.items():
            chil.clean()

    def compare(self, ty_bags):

        if len(self.vars) != len(ty_bags.vars) or len(self.children) != len(
            ty_bags.children
        ):
            return False

        for (key1, value1), (key2, value2) in zip(
            self.vars.items(), ty_bags.vars.items()
        ):
            if key1 != key2 or value1 != value2:
                return False
        for (key1, value1), (key2, value2) in zip(
            self.children.items(), ty_bags.children.items()
        ):
            if key1 != key2 or not value1.compare(value2):
                return False
        return True

    def clone(self, ty_bags):
        self.parent = ty_bags.parent
        for key, value in ty_bags.vars.items():
            self.vars[key] = value.copy()
        for key, value in ty_bags.children.items():
            new_ty = TyBags()
            new_ty.clone(value)
            self.children[key] = new_ty
