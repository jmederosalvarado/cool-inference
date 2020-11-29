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

    def reduce_bag(self, node, types, name=None):

        # TODO: preguntar especificamente el tipo del nodo
        try:
            var_name = node.id
        except AttributeError:
            if name is not None:
                var_name = name
            else:
                return

        types = types.copy()
        if "@lock" in types:
            types.remove("@lock")
        types = set(types)

        var_types = self.find_variable(var_name)

        if "@lock" in var_types:
            return

        intersection = var_types.intersection(types)

        if len(intersection) == 0:
            self.modify_variable(var_name, set.union(var_types, types, {"@union"}))

        else:
            # TODO: revisar estos casos
            if "@union" in var_types:
                self.modify_variable(var_name, set.union(var_types, types))
            elif "@union" in types:
                self.modify_variable(var_name, types)
            else:
                self.modify_variable(var_name, intersection)

    def define_variable(self, name, types, lock=False):
        if lock:
            self.vars[name] = set.union(set(types), {"@lock"})
        else:
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
            self.vars[name] = set(types)
        except KeyError as e:
            if self.parent is not None:
                self.parent.modify_variable(name, types)
            else:
                raise e

    # este nombre esta al berro
    def clean(self):
        for _, value in self.vars.items():
            if "@union" in value:
                value.remove("@union")
        for _, chil in self.children.items():
            chil.clean()

    def clean_locks(self):
        for _, value in self.vars.items():
            if "@lock" in value:
                value.remove("@lock")
        for _, chil in self.children.items():
            chil.clean_locks()

    # TODO: creo que esto esta maja
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

    # TODO: este metodo deberia devolver un nuevo tybag igual a self
    def clone(self, ty_bags):
        self.parent = ty_bags.parent
        for key, value in ty_bags.vars.items():
            self.vars[key] = value.copy()
        for key, value in ty_bags.children.items():
            new_ty = TyBags()
            new_ty.clone(value)
            self.children[key] = new_ty
