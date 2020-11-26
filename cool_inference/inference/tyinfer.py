from cool_inference.inference.tybags import TyBags
from cool_inference.utils.lca import lowest_common_ancestor
import cool_inference.utils.visitor as visitor
from cool_inference.semantics.semantics import (
    IntType,
    BoolType,
    StringType,
    AutoType,
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
    Binary,
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

        tybags.define_variable("self", [self.current_type.name])

        # TODO: hacer esto en el visit de FuncDecl
        for method in self.current_type.methods:
            if method.return_type == AutoType():
                types = set(self.context.types.keys())
            else:
                types = [method.return_type.name]
            tybags.define_variable(method.name, types)

        # TODO: hacer esto en el visit de AttrDecl
        for attr in self.current_type.attributes:
            if attr.type == AutoType():
                types = set(self.context.types.keys())
            else:
                types = [attr.type.name]
            tybags.define_variable(attr.name, types)

        for feat in node.feature_list:
            self.visit(feat, tybags)

        return tybags

    @visitor.when(FuncDecl)
    def visit(self, node, tybags):  # noqa: F811
        self.current_method = self.current_type.get_method(node.id)
        method_tybags = tybags.create_child(node)

        for pname, ptype in zip(
            self.current_method.param_names, self.current_method.param_types
        ):
            if ptype == AutoType():
                method_tybags.define_variable(pname, set(self.context.types.keys()))
            else:
                method_tybags.define_variable(pname, [ptype.name])

        self.visit(node.body, method_tybags)

        self.current_method = None

    @visitor.when(LetIn)
    def visit(self, node, tybags):  # noqa: F811
        let_tybags = tybags.create_child(node)
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, _ in decl_list:
            typex = self.context.get_type(_type)

            if typex == AutoType():
                let_tybags.define_variable(idx, set(self.context.types.keys()))
            else:
                let_tybags.define_variable(idx, [typex.name])

        self.visit(exp, let_tybags)

    # TODO
    @visitor.when(Case)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

        for idx, typex, case_exp in node.case_list:

            new_tybags = tybags.create_child(case_exp)

            typex = self.context.get_type(typex)

            if typex == AutoType():
                new_tybags.define_variable(idx, set(self.context.types.keys()))
            else:
                new_tybags.define_variable(idx, [typex.name])

            self.visit(case_exp, new_tybags)

    @visitor.when(Block)
    def visit(self, node, tybags):  # noqa: F811
        for exp in node.expr_list:
            self.visit(exp, tybags)

    @visitor.when(Not)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    # TODO
    @visitor.when(Tilde)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(IsVoid)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(ParenthExp)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(Binary)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.left, tybags)
        self.visit(node.right, tybags)

    @visitor.when(IfThenElse)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.first, tybags)
        self.visit(node.second, tybags)
        self.visit(node.third, tybags)


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
        print(tybags.compare(self.tybags))

        while not self.tybags.compare(tybags):
            tybags.clone(self.tybags)

            for cool_class in node.cool_class_list:
                self.visit(cool_class, self.tybags, [])
            self.tybags.clean()

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
        types = self.visit(
            node.value,
            tybags,
            []
            if tybags.find_variable(node.id) is None
            else tybags.find_variable(node.id),
        )

        tybags.reduce_bag(node, types)
        return tybags.find_variable(node.id)

    # TODO fix dispatch. Find an elegant way to do it.
    @visitor.when(Dispatch)
    def visit(self, node, tybags, restriction):  # noqa: F811
        exp_type = self.context.types[list(self.visit(node.exp, tybags, []))[0]]

        for arg in node.exp_list:
            arg_types = self.visit(arg, tybags, [])
            tybags.reduce_bag(arg, arg_types)

        while tybags.parent is not None:
            tybags = tybags.parent

        for _, ty in tybags.children.items():

            if list(ty.vars["self"])[0] == exp_type.name:
                tybags = ty
                break

        return tybags.find_variable(node.id)

    # TODO
    @visitor.when(StaticDispatch)
    def visit(self, node, tybags, restriction):  # noqa: F811
        pass

    @visitor.when(LetIn)
    def visit(self, node, tybags, restriction):  # noqa: F811
        let_tybags = tybags.children[node]
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, expx in decl_list:
            # typex = self.context.get_type(_type)

            if expx is not None:
                tybags.reduce_bag(node, self.visit(expx, tybags, []))

        let_types = self.visit(exp, let_tybags, [])

        return let_types

    # TODO
    @visitor.when(Case)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, [])
        return_types = []
        ances_type = None

        for idx, typex, case_exp in node.case_list:

            new_tybags = tybags.children[case_exp]

            typex = self.context.get_type(typex)

            static_types = self.visit(case_exp, new_tybags, [])

            if len(static_types) == 0:
                ances_type = lowest_common_ancestor(
                    ances_type, self.context.get_type[static_types[0]], self.context
                )

            else:
                return_types = set.union(set(return_types), set(static_types))

        return set.union(set(return_types), set([ances_type.name]))

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
        _ = self.visit(node.exp, tybags, [])

        return set([BoolType().name])

    # TODO
    @visitor.when(Tilde)
    def visit(self, node, tybags, restriction):  # noqa: F811
        pass

    @visitor.when(IsVoid)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, [])
        return set([BoolType().name])

    @visitor.when(ParenthExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        self.visit(node.exp, tybags, [])

    def arith(self, node, tybags):
        _ = self.visit(node.left, tybags, [IntType().name])
        _ = self.visit(node.right, tybags, [IntType().name])
        tybags.reduce_bag(node.left, [IntType().name])
        tybags.reduce_bag(node.right, [IntType().name])
        return set([IntType().name])

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
        return set([BoolType().name])

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
        _ = self.visit(node.left, tybags, [BoolType().name])
        _ = self.visit(node.right, tybags, [])

        return set([self.context.get_type("Object").name])

    @visitor.when(IfThenElse)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.first, tybags, [BoolType().name])
        then_types = self.visit(node.second, tybags, [])
        else_types = self.visit(node.third, tybags, [])

        inters = then_types & else_types

        if len(inters) > 0:
            return inters

        return set.union(then_types, else_types)

    @visitor.when(StringExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([StringType().name])

    @visitor.when(BoolExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([BoolType().name])

    @visitor.when(IntExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([IntType().name])

    @visitor.when(IdExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return tybags.find_variable(node.id)

    @visitor.when(NewType)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([node.type])
