from cool_inference.inference.tybags import TyBags
from cool_inference.utils.lca import solve_bag
import cool_inference.utils.visitor as visitor
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


class BagsCollector:
    def __init__(self, context, errors=[]):
        self.context = context
        self.errors = errors

        self.all_types = list(self.context.types.keys())
        self.all_types.remove("AUTO_TYPE")
        self.all_types = set(self.all_types)

        io_tybags = TyBags()
        io_tybags.define_variable("out_int", {"SELF_TYPE"})
        io_tybags.define_variable("out_string", {"SELF_TYPE"})
        io_tybags.define_variable("in_int", {"Int"})
        io_tybags.define_variable("in_string", {"String"})
        io = context.get_type("IO")
        met = io.get_method("out_int")
        met.tybags = io_tybags.create_child("out_int")
        met.tybags.define_variable("x", {"SELF_TYPE"})
        met = io.get_method("out_string")
        met.tybags = io_tybags.create_child("out_string")
        met.tybags.define_variable("x", {"SELF_TYPE"})
        met = io.get_method("in_string")
        met = io.get_method("in_int")

    @visitor.on("node")
    def visit(self, node, bags):
        pass

    @visitor.when(Program)
    def visit(self, node, tybags=None):  # noqa: F811
        tybags = TyBags()

        for cool_class in node.cool_class_list:
            self.visit(cool_class, tybags)
        return tybags

    @visitor.when(CoolClass)
    def visit(self, node, tybags):  # noqa: F811
        tybags = tybags.create_child(node)

        self.current_type = self.context.get_type(node.id)

        tybags.define_variable("self", [self.current_type.name], True)

        for method in self.current_type.methods:
            if method.return_type.name == "AUTO_TYPE":
                types = self.all_types
                tybags.define_variable(method.name, types)
            else:
                types = [method.return_type.name]
                tybags.define_variable(method.name, types, True)

        for attr in self.current_type.attributes:
            if attr.type.name == "AUTO_TYPE":
                types = self.all_types
                tybags.define_variable(attr.name, types)
            else:
                types = [attr.type.name]

                tybags.define_variable(attr.name, types, True)

        for feat in node.feature_list:
            self.visit(feat, tybags)

        return tybags

    @visitor.when(AttrDecl)
    def visit(self, node, tybags):  # noqa: F811
        if node.body is not None:
            self.visit(node.body, tybags)

    @visitor.when(FuncDecl)
    def visit(self, node, tybags):  # noqa: F811
        self.current_method = self.current_type.get_method(node.id)
        method_tybags = tybags.create_child(node)
        self.current_method.tybags = method_tybags

        for pname, ptype in zip(
            self.current_method.param_names, self.current_method.param_types
        ):
            if ptype.name == "AUTO_TYPE":
                method_tybags.define_variable(pname, self.all_types)
            else:
                method_tybags.define_variable(pname, [ptype.name], True)

        self.visit(node.body, method_tybags)

        self.current_method = None

    @visitor.when(Assign)
    def visit(self, node, tybags):  # noqa: F811
        if node.value is not None:
            self.visit(node.value, tybags)

    @visitor.when(Dispatch)
    def visit(self, node, tybags):  # noqa: F811
        if node.exp is not None:
            self.visit(node.exp, tybags)

    @visitor.when(StaticDispatch)
    def visit(self, node, tybags):  # noqa: F811
        if node.exp is not None:
            self.visit(node.exp, tybags)

    @visitor.when(LetIn)
    def visit(self, node, tybags):  # noqa: F811
        let_tybags = tybags.create_child(node)
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, _ in decl_list:
            typex = self.context.get_type(_type)

            if typex.name == "AUTO_TYPE":
                let_tybags.define_variable(idx, self.all_types)
            else:
                let_tybags.define_variable(idx, [typex.name], True)

        self.visit(exp, let_tybags)

    @visitor.when(Case)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

        for idx, typex, case_exp in node.case_list:

            new_tybags = tybags.create_child(case_exp)

            typex = self.context.get_type(typex)

            if typex.name == "AUTO_TYPE":
                new_tybags.define_variable(idx, self.all_types)
            else:
                new_tybags.define_variable(idx, [typex.name], True)

            self.visit(case_exp, new_tybags)

    @visitor.when(Block)
    def visit(self, node, tybags):  # noqa: F811
        for exp in node.expr_list:
            self.visit(exp, tybags)

    @visitor.when(Not)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(Tilde)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(IsVoid)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(ParenthExp)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    def binary_visit(self, node, tybags):
        self.visit(node.left, tybags)
        self.visit(node.right, tybags)

    @visitor.when(Plus)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Minus)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Div)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Mult)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Leq)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Eq)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Le)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(WhileLoop)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(IfThenElse)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.first, tybags)
        self.visit(node.second, tybags)
        self.visit(node.third, tybags)

    @visitor.when(StringExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(BoolExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(IntExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(IdExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(NewType)
    def visit(self, node, tybags):  # noqa: F811
        pass


class BagsReducer:
    def __init__(self, tybags, context, errors=[]):
        self.current_type = None
        self.current_method = None
        self.context = context
        self.errors = errors
        self.tybags = tybags

    @visitor.on("node")
    def visit(self, node, tybags, restriction):
        pass

    @visitor.when(Program)
    def visit(self, node, tybags=None, restriction=None):  # noqa: F811
        tybags = TyBags()

        while not self.tybags.compare(tybags):

            tybags.clone(self.tybags)

            for cool_class in node.cool_class_list:
                self.visit(cool_class, self.tybags, [])

        self.tybags.clean()
        self.tybags.clean_locks()
        return self.tybags

    @visitor.when(CoolClass)
    def visit(self, node, tybags, restriction):  # noqa: F811
        self.current_type = self.context.get_type(node.id)
        tybags = tybags.children[node]

        for feat in node.feature_list:
            self.visit(feat, tybags, [])
        self.current_type = None

    @visitor.when(AttrDecl)
    def visit(self, node, tybags, restriction):  # noqa: F811
        if node.body is not None:
            tybags.reduce_bag(node, self.visit(node.body, tybags, []))

    @visitor.when(FuncDecl)
    def visit(self, node, tybags, restriction):  # noqa: F811
        self.current_method = self.current_type.get_method(node.id)
        method_tybags = tybags.children[node]

        return_types = self.visit(node.body, method_tybags, [])

        method_tybags.reduce_bag(node, return_types)

        self.current_method = None

    @visitor.when(Assign)
    def visit(self, node, tybags, restriction):  # noqa: F811
        types = self.visit(node.value, tybags, [])

        tybags.reduce_bag(node, types)

        if len(restriction) > 0:
            tybags.reduce_bag(node, restriction)

        return tybags.find_variable(node.id)

    @visitor.when(Dispatch)
    def visit(self, node, tybags, restriction):  # noqa: F811
        exp_types = self.visit(node.exp, tybags, [])
        if "@lock" in exp_types:
            exp_types.remove("@lock")

        if len(exp_types) > 1:
            types_whith_method = []
            return_types = set([])
            for key, value in self.context.types.items():
                for method in value.methods:
                    if (
                        key in exp_types
                        and method.name == node.id
                        and len(method.param_names) == len(node.exp_list)
                    ):
                        types_whith_method.append(key)
                        return_types = set.union(
                            return_types, (method.tybags.parent.vars[method.name])
                        )
                        break

            if len(types_whith_method) == 0:
                error = f"""
                There is not possible type of expression that
                have {node.id} method with {len(node.exp_list)} params
                """
                if error not in self.errors:
                    self.errors.append(error)

                return {"ERROR"}

            tybags.reduce_bag(node.exp, types_whith_method)

            result = return_types

        elif len(exp_types) == 1:
            exp_type = self.context.types[list(exp_types)[0]]
            method = exp_type.get_method(node.id)
            function_ty = method.tybags

            for arg, param in zip(node.exp_list, method.param_names):
                arg_types = self.visit(arg, tybags, function_ty.vars[param])
                function_ty.reduce_bag(None, arg_types, name=param)

            result = function_ty.find_variable(node.id)

        if "SELF_TYPE" in result:

            result.remove("SELF_TYPE")
            result = set.union(result, {self.current_type.name})

        return result

    @visitor.when(StaticDispatch)
    def visit(self, node, tybags, restriction):  # noqa: F811
        exp_types = self.visit(node.exp, tybags, [])
        if "@lock" in exp_types:
            exp_types.remove("@lock")

        if len(exp_types) > 1:
            types_whith_method = []
            return_types = set([])
            for key, value in self.context.types.items():
                for method in value.methods:
                    if (
                        key in exp_types
                        and method.name == node.id
                        and len(method.param_names) == len(node.exp_list)
                    ):
                        types_whith_method.append(key)
                        return_types = set.union(
                            return_types, (method.tybags.parent.vars[method.name])
                        )
                        break

            if len(types_whith_method) == 0:
                error = f"""
                There is not possible type of expression that
                have {node.id} method with {len(node.exp_list)} params
                """
                if error not in self.errors:
                    self.errors.append(error)

                return {"ERROR"}

            tybags.reduce_bag(node.exp, types_whith_method)

            result = return_types

        elif len(exp_types) == 1:
            exp_type = self.context.types[list(exp_types)[0]]
            method = exp_type.get_method(node.id)

            function_ty = method.tybags

            for arg, param in zip(node.exp_list, method.param_names):
                arg_types = self.visit(arg, tybags, function_ty.vars[param])
                function_ty.reduce_bag(None, arg_types, name=param)

            result = function_ty.find_variable(node.id)

        if "SELF_TYPE" in result:

            result.remove("SELF_TYPE")
            result = set.union(result, {self.current_type.name})

        return result

    @visitor.when(LetIn)
    def visit(self, node, tybags, restriction):  # noqa: F811
        let_tybags = tybags.children[node]
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, expx in decl_list:

            if expx is not None:
                let_tybags.reduce_bag(
                    None, self.visit(expx, let_tybags, [_type]), name=idx
                )

        let_types = self.visit(exp, let_tybags, [])

        return let_types

    @visitor.when(Case)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, [])
        return_types = set([])

        for idx, typex, case_exp in node.case_list:

            new_tybags = tybags.children[case_exp]

            typex = self.context.get_type(typex)

            static_types = self.visit(case_exp, new_tybags, [])

            return_types = set.union(return_types, static_types)

        return return_types

    @visitor.when(Block)
    def visit(self, node, tybags, restriction):  # noqa: F811
        li = []
        for exp in node.expr_list[0 : len(node.expr_list) - 1]:
            exp_types = self.visit(exp, tybags, li)

        last = node.expr_list[len(node.expr_list) - 1]
        exp_types = self.visit(last, tybags, restriction)
        if len(restriction) > 0:
            tybags.reduce_bag(last, restriction)

        return exp_types

    @visitor.when(Not)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, ["Bool"])

        return set(["Bool"])

    @visitor.when(Tilde)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, ["Int"])
        tybags.reduce_bag(node.exp, ["Int"])
        return set(["Int"])

    @visitor.when(IsVoid)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, [])
        return set(["Bool"])

    @visitor.when(ParenthExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        self.visit(node.exp, tybags, restriction)

    def arith(self, node, tybags):
        _ = self.visit(node.left, tybags, ["Int"])
        _ = self.visit(node.right, tybags, ["Int"])
        tybags.reduce_bag(node.left, ["Int"])
        tybags.reduce_bag(node.right, ["Int"])
        return set(["Int"])

    @visitor.when(Plus)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    @visitor.when(Minus)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    @visitor.when(Div)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    @visitor.when(Mult)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    def comp(self, node, tybags):
        _ = self.visit(node.left, tybags, [])
        _ = self.visit(node.right, tybags, [])
        return set(["Bool"])

    @visitor.when(Leq)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.comp(node, tybags)

    @visitor.when(Eq)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.comp(node, tybags)

    @visitor.when(Le)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.comp(node, tybags)

    @visitor.when(WhileLoop)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.left, tybags, ["Bool"])
        _ = self.visit(node.right, tybags, [])

        return set([self.context.get_type("Object").name])

    @visitor.when(IfThenElse)
    def visit(self, node, tybags, restriction):  # noqa: F811
        types = self.visit(node.first, tybags, ["Bool"])
        tybags.reduce_bag(node.first, types)
        then_types = self.visit(node.second, tybags, [])
        else_types = self.visit(node.third, tybags, [])
        intersection = then_types & else_types
        if len(intersection) > 0:
            return intersection
        return set.union(then_types, else_types)

    @visitor.when(StringExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set(["String"])

    @visitor.when(BoolExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set(["Bool"])

    @visitor.when(IntExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set(["Int"])

    @visitor.when(IdExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        if len(restriction) > 0:
            tybags.reduce_bag(node, restriction)

        return tybags.find_variable(node.id)

    @visitor.when(NewType)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([node.type])


class BagsReplacer:
    def __init__(self, tybags, context, errors=[]):
        self.current_type = None
        self.current_method = None
        self.context = context
        self.errors = errors
        self.tybags = tybags

    @visitor.on("node")
    def visit(self, node, tybags):
        pass

    @visitor.when(Program)
    def visit(self, node, tybags=None):  # noqa: F811
        for cool_class in node.cool_class_list:
            self.visit(cool_class, self.tybags)

    @visitor.when(CoolClass)
    def visit(self, node, tybags):  # noqa: F811
        self.current_type = self.context.get_type(node.id)
        tybags = tybags.children[node]

        for feat in node.feature_list:
            self.visit(feat, tybags)
        self.current_type = None

    @visitor.when(AttrDecl)
    def visit(self, node, tybags):  # noqa: F811
        node.type = solve_bag(tybags.vars[node.id], self.context)
        if node.body is not None:
            self.visit(node.body, tybags)

    @visitor.when(FuncDecl)
    def visit(self, node, tybags):  # noqa: F811
        self.current_method = self.current_type.get_method(node.id)
        method_tybags = tybags.children[node]

        self.visit(node.body, method_tybags)
        node.type = solve_bag(tybags.vars[node.id], self.context)
        for param in node.params:
            param.type = solve_bag(method_tybags.vars[param.id], self.context)

        self.current_method = None

    @visitor.when(Assign)
    def visit(self, node, tybags):  # noqa: F811
        if node.value is not None:
            self.visit(node.value, tybags)

    @visitor.when(Dispatch)
    def visit(self, node, tybags):  # noqa: F811
        if node.exp is not None:
            self.visit(node.exp, tybags)

    @visitor.when(StaticDispatch)
    def visit(self, node, tybags):  # noqa: F811
        if node.exp is not None:
            self.visit(node.exp, tybags)

    @visitor.when(LetIn)
    def visit(self, node, tybags):  # noqa: F811
        let_tybags = tybags.children[node]
        decl_list, exp = node.decl_list, node.exp

        new_decl_list = []

        for idx, _type, expx in decl_list:
            new_decl_list.append(
                (idx, solve_bag(let_tybags.vars[idx], self.context), expx)
            )

        node.decl_list = new_decl_list
        self.visit(exp, let_tybags)

    @visitor.when(Case)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

        new_case_list = []

        for idx, typex, case_exp in node.case_list:

            new_tybags = tybags.children[case_exp]

            new_case_list.append(
                (idx, solve_bag(new_tybags.vars[idx], self.context), case_exp)
            )

            self.visit(case_exp, new_tybags)
        node.case_list = new_case_list

    @visitor.when(Block)
    def visit(self, node, tybags):  # noqa: F811
        for exp in node.expr_list:
            self.visit(exp, tybags)

    @visitor.when(Not)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(Tilde)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(IsVoid)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(ParenthExp)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    def binary_visit(self, node, tybags):
        self.visit(node.left, tybags)
        self.visit(node.right, tybags)

    @visitor.when(Plus)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Minus)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Div)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Mult)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Leq)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Eq)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(Le)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(WhileLoop)
    def visit(self, node, tybags):  # noqa: F811
        self.binary_visit(node, tybags)

    @visitor.when(IfThenElse)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.first, tybags)
        self.visit(node.second, tybags)
        self.visit(node.third, tybags)

    @visitor.when(StringExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(BoolExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(IntExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(IdExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(NewType)
    def visit(self, node, tybags):  # noqa: F811
        pass
