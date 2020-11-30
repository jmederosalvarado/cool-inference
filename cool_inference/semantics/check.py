import cool_inference.utils.visitor as visitor
from cool_inference.utils.lca import lowest_common_ancestor
from cool_inference.semantics.semantics import (
    SemanticError,
    ErrorType,
    Context,
    Scope,
    IntType,
    BoolType,
    StringType,
    AutoType,
    ObjectType,
    SelfType,
    IOType,
)
from cool_inference.ast import (
    Program,
    CoolClass,
    FuncDecl,
    AttrDecl,
    Assign,
    Not,
    IsVoid,
    Tilde,
    Dispatch,
    StaticDispatch,
    IfThenElse,
    WhileLoop,
    LetIn,
    Case,
    NewType,
    ParenthExp,
    IdExp,
    Block,
    IntExp,
    StringExp,
    BoolExp,
    Plus,
    Minus,
    Mult,
    Div,
    Le,
    Leq,
    Eq,
)

WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'
INVALID_COMPARISSON = 'Comparison is not defined between "%s" and "%s".'
BOOL_EXPECTED = 'Was expected a bool, not "%s".'
STATIC_DISPATCH_ERROR = 'Type "%s" is not descendent of "%s"'


class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program)
    def visit(self, node):  # noqa: F811
        self.context = Context()

        object_type = ObjectType()
        self.context.types["Object"] = object_type

        int_type = IntType()
        int_type.set_parent(object_type)
        self.context.types["Int"] = int_type

        bool_type = BoolType()
        bool_type.set_parent(object_type)
        self.context.types["Bool"] = bool_type

        string_type = StringType()
        string_type.set_parent(object_type)
        self.context.types["String"] = string_type

        error_type = ErrorType()
        error_type.set_parent(object_type)
        self.context.types["ERROR"] = error_type

        auto_type = AutoType()
        auto_type.set_parent(object_type)
        self.context.types["AUTO_TYPE"] = auto_type

        self_type = SelfType()
        self_type.set_parent(object_type)
        self.context.types["SELF_TYPE"] = self_type

        io_type = IOType()
        io_type.set_parent(object_type)
        self.context.types["IO"] = io_type

        for cl in node.cool_class_list:
            self.visit(cl)

    @visitor.when(CoolClass)
    def visit(self, node):  # noqa: F811
        try:
            self.context.create_type(node.id)
        except SemanticError as err:
            self.errors.append(err.text)


class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors

    @visitor.on("node")
    def visit(self, node):  # noqa: F811
        pass

    @visitor.when(Program)
    def visit(self, node):  # noqa: F811
        for cool_class in node.cool_class_list:
            self.visit(cool_class)

    @visitor.when(CoolClass)
    def visit(self, node):  # noqa: F811
        self.current_type = self.context.get_type(node.id)

        parent_type = self.context.get_type("Object")

        if node.inherit is not None:
            try:
                _type = self.context.get_type(node.inherit)
            except SemanticError as error:
                _type = self.context.get_type("ERROR")
                self.errors.append(error.text)
            parent_type = _type

        try:
            self.current_type.set_parent(parent_type)
        except SemanticError as e:
            self.errors.append(e.text)

        for feat in node.feature_list:
            self.visit(feat)

    @visitor.when(AttrDecl)
    def visit(self, node):  # noqa: F811
        try:
            _type = self.context.get_type(node.type)
        except SemanticError as error:
            _type = self.context.get_type("ERROR")
            self.errors.append(error.text)

        try:
            self.current_type.define_attribute(node.id, _type)
        except SemanticError as error:
            self.errors.append(error.text)

    @visitor.when(FuncDecl)
    def visit(self, node):  # noqa: F811
        param_names = [param.id for param in node.params]
        param_types_names = [param.type for param in node.params]
        param_types = []
        for p in param_types_names:
            try:
                _type = self.context.get_type(p)
            except SemanticError as error:
                _type = self.context.get_type("ERROR")
                self.errors.append(error.text)
            param_types.append(_type)

        try:
            _type = self.context.get_type(node.type)
        except SemanticError as error:
            _type = self.context.get_type("ERROR")
            self.errors.append(error.text)
        return_type = _type

        try:
            self.current_type.define_method(
                node.id, param_names, param_types, return_type
            )
        except SemanticError as e:
            self.errors.append(e.text)


class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors

    @visitor.on("node")
    def visit(self, node, scope):
        pass

    @visitor.when(Program)
    def visit(self, node, scope=None):  # noqa: F811
        scope = Scope()
        for cool_class in node.cool_class_list:
            self.visit(cool_class, scope.create_child())
        return scope

    @visitor.when(CoolClass)
    def visit(self, node, scope):  # noqa: F811
        self.current_type = self.context.get_type(node.id)
        scope.define_variable("self", self.current_type)
        for attr in self.current_type.attributes:
            scope.define_variable(attr.name, attr.type)

        for feat in node.feature_list:
            self.visit(feat, scope)
        self.current_type = None

    @visitor.when(AttrDecl)
    def visit(self, node, scope):  # noqa: F811
        if node.body is not None:
            exp_type = self.visit(node.body, scope)
            node_type = self.context.get_type(node.type)

            if exp_type.name == "SELF_TYPE" and not node_type.conforms_to(
                self.exp_type
            ):
                self.errors.append(
                    INCOMPATIBLE_TYPES % (node_type.name, self.exp_type.name)
                )

            elif exp_type.name != "SELF_TYPE" and not node_type.conforms_to(exp_type):
                self.errors.append(INCOMPATIBLE_TYPES % (node_type.name, exp_type.name))

    @visitor.when(FuncDecl)
    def visit(self, node, scope):  # noqa: F811
        self.current_method = self.current_type.get_method(node.id)
        method_scope = scope.create_child()

        for pname, ptype in zip(
            self.current_method.param_names, self.current_method.param_types
        ):
            method_scope.define_variable(pname, ptype)

        return_type = self.visit(node.body, method_scope)

        if (
            self.current_method.return_type.name == "SELF_TYPE"
            and not return_type.conforms_to(self.current_type)
        ):
            self.errors.append(
                INCOMPATIBLE_TYPES % (return_type.name, self.current_type.name)
            )

        elif (
            self.current_method.return_type.name != "SELF_TYPE"
            and not return_type.conforms_to(self.current_method.return_type)
        ):
            self.errors.append(
                INCOMPATIBLE_TYPES
                % (return_type.name, self.current_method.return_type.name)
            )

        if self.current_type.parent is not None:
            try:
                parent_method = self.current_type.parent.get_method(
                    self.current_method.name
                )
                if parent_method != self.current_method:
                    self.errors.append(WRONG_SIGNATURE % (parent_method.name, "parent"))
            except SemanticError:
                pass

        self.current_method = None

    @visitor.when(Dispatch)
    def visit(self, node, scope):  # noqa: F811
        exp_type = self.visit(node.exp, scope)
        if exp_type.name == "AUTO_TYPE":
            return exp_type

        try:
            method = exp_type.get_method(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            return self.context.get_type("ERROR")

        if len(node.exp_list) != len(method.param_names):
            self.errors.append(
                "Method %s takes %d arguments but %d were given"
                % (method.name, len(method.param_names), len(node.exp_list))
            )

        for arg, ptype in zip(node.exp_list, method.param_types):
            arg_type = self.visit(arg, scope)
            if not arg_type.conforms_to(ptype):
                self.errors.append(INCOMPATIBLE_TYPES % (arg_type.name, ptype.name))

        result = method.return_type

        if result.name == "SELF_TYPE":
            result = exp_type

        return result

    @visitor.when(StaticDispatch)
    def visit(self, node, scope):  # noqa: F811
        exp_type = self.visit(node.exp, scope)
        try:
            method = exp_type.get_method(node.id)
        except SemanticError as e:
            self.errors.append(e.text)
            return self.context.get_type("ERROR")

        if len(node.exp_list) != len(method.param_names):
            self.errors.append(
                "Method %s takes %d arguments but %d were given"
                % (method.name, len(method.param_names), len(node.exp_list))
            )

        for arg, ptype in zip(node.exp_list, method.param_types):
            arg_type = self.visit(arg, scope)
            if not arg_type.conforms_to(ptype):
                self.errors.append(INCOMPATIBLE_TYPES % (arg_type.name, ptype.name))

        try:
            specific_type = self.context.get_type(node.specific_type)
            if not exp_type.conforms_to(specific_type):
                self.errors.append(STATIC_DISPATCH_ERROR % (exp_type, specific_type))
        except SemanticError as e:
            self.errors.append(e.text)

        return method.return_type

    @visitor.when(LetIn)
    def visit(self, node, scope):  # noqa: F811
        let_scope = scope.create_child()
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, expx in decl_list:
            try:
                typex = self.context.get_type(_type)
            except SemanticError as e:
                typex = self.context.get_type("ERROR")
                self.errors.append(e.text)

            if expx is None:
                right_type = typex
            else:
                right_type = self.visit(expx, scope)

            if typex.name == "SELF_TYPE" and not right_type.conforms_to(
                self.current_type
            ):
                self.errors.append(
                    INCOMPATIBLE_TYPES % (right_type.name, self.current_type.name)
                )

            elif typex.name != "SELF_TYPE" and not right_type.conforms_to(typex):
                self.errors.append(INCOMPATIBLE_TYPES % (right_type.name, typex.name))

            let_scope.define_variable(idx, typex)

        let_type = self.visit(exp, let_scope)

        return let_type

    @visitor.when(Case)
    def visit(self, node, scope):  # noqa: F811
        _ = self.visit(node.exp, scope)
        return_type = None
        first = True

        for idx, _type, case_exp in node.case_list:
            try:
                typex = self.context.get_type(_type)
            except SemanticError as e:
                typex = self.context.get_type("ERROR")
                self.errors.append(e.text)

            new_scope = scope.create_child()
            new_scope.define_variable(idx, typex)
            static_type = self.visit(case_exp, new_scope)

            if first:
                return_type = static_type
                first = False
            else:
                return_type = lowest_common_ancestor(
                    return_type, static_type, self.context
                )

        return return_type

    @visitor.when(Block)
    def visit(self, node, scope):  # noqa: F811

        for exp in node.expr_list:
            exp_type = self.visit(exp, scope)
        return exp_type

    @visitor.when(Assign)
    def visit(self, node, scope):  # noqa: F811
        if node.id == "self":
            self.errors.append(SELF_IS_READONLY)

        var = scope.find_variable(node.id)
        if var is None:
            self.errors.append(
                VARIABLE_NOT_DEFINED % (node.id, self.current_method.name)
            )
            var_type = self.context.get_type("ERROR")
        else:
            var_type = var.type

        right_type = self.visit(node.value, scope)
        if not right_type.conforms_to(var_type):
            self.errors.append(INCOMPATIBLE_TYPES % (right_type.name, var_type.name))

        return var_type

    @visitor.when(Not)
    def visit(self, node, scope):  # noqa: F811
        exp_type = self.visit(node.exp, scope)
        bool_type = self.context.get_type("Bool")
        if exp_type != bool_type:
            self.errors.append(BOOL_EXPECTED % (exp_type))

        return bool_type

    @visitor.when(Tilde)
    def visit(self, node, scope):  # noqa: F811
        exp_type = self.visit(node.exp, scope)
        int_type = self.context.get_type("Int")
        if not exp_type.conforms_to(int_type):
            self.errors.append(INCOMPATIBLE_TYPES % (exp_type, int_type))
        return int_type

    @visitor.when(IsVoid)
    def visit(self, node, scope):  # noqa: F811
        _ = self.visit(node.exp, scope)
        return self.context.get_type("Bool")

    @visitor.when(ParenthExp)
    def visit(self, node, scope):  # noqa: F811
        return self.visit(node.exp, scope)

    def arith(self, node, scope):
        int_type = self.context.get_type("Int")
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if not left_type.conforms_to(int_type) or not right_type.conforms_to(int_type):
            self.errors.append(INVALID_OPERATION % (left_type.name, right_type.name))
        return int_type

    @visitor.when(Plus)
    def visit(self, node, scope):  # noqa: F811
        return self.arith(node, scope)

    @visitor.when(Minus)
    def visit(self, node, scope):  # noqa: F811
        return self.arith(node, scope)

    @visitor.when(Div)
    def visit(self, node, scope):  # noqa: F811
        return self.arith(node, scope)

    @visitor.when(Mult)
    def visit(self, node, scope):  # noqa: F811
        return self.arith(node, scope)

    def comp(self, node, scope):
        left_type = self.visit(node.left, scope)
        right_type = self.visit(node.right, scope)
        if not left_type.conforms_to(right_type) and not right_type.conforms_to(
            left_type
        ):
            self.errors.append(INVALID_COMPARISSON % (left_type.name, right_type.name))
        return self.context.get_type("Bool")

    @visitor.when(Leq)
    def visit(self, node, scope):  # noqa: F811
        return self.comp(node, scope)

    @visitor.when(Eq)
    def visit(self, node, scope):  # noqa: F811
        return self.comp(node, scope)

    @visitor.when(Le)
    def visit(self, node, scope):  # noqa: F811
        return self.comp(node, scope)

    @visitor.when(WhileLoop)
    def visit(self, node, scope):  # noqa: F811
        conditional_type = self.visit(node.left, scope)
        _ = self.visit(node.right, scope)

        if conditional_type != self.context.get_type("Bool"):
            self.errors.append(BOOL_EXPECTED % (conditional_type))

        return self.context.get_type("Object")

    @visitor.when(IfThenElse)
    def visit(self, node, scope):  # noqa: F811
        conditional_type = self.visit(node.first, scope)
        then_type = self.visit(node.second, scope)
        else_type = self.visit(node.third, scope)
        bool_type = self.context.get_type("Bool")

        if not conditional_type.conforms_to(bool_type):
            self.errors.append(BOOL_EXPECTED % (conditional_type))

        return lowest_common_ancestor(then_type, else_type, self.context)

    @visitor.when(StringExp)
    def visit(self, node, scope):  # noqa: F811
        return self.context.get_type("String")

    @visitor.when(BoolExp)
    def visit(self, node, scope):  # noqa: F811
        return self.context.get_type("Bool")

    @visitor.when(IntExp)
    def visit(self, node, scope):  # noqa: F811
        return self.context.get_type("Int")

    @visitor.when(IdExp)
    def visit(self, node, scope):  # noqa: F811
        var = scope.find_variable(node.id)
        if var is None:
            self.errors.append(
                VARIABLE_NOT_DEFINED % (node.id, self.current_method.name)
            )
            return self.context.get_type("ERROR")

        return var.type

    @visitor.when(NewType)
    def visit(self, node, scope):  # noqa: F811
        if node.type == "SELF_TYPE":
            return self.current_type
        return self.context.get_type(node.type)
