from cool_inference.inference.ty_bags import TyBags
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
    def visit(self, node, ty_bags=None):
        ty_bags = TyBags()

        for cool_class in node.cool_class_list:
            self.visit(cool_class, ty_bags)
        return ty_bags

    @visitor.when(CoolClass)
    def visit(self, node, ty_bags):
        ty_bags = ty_bags.create_child(node)

        self.current_type = self.context.get_type(node.id)

        ty_bags.define_variable("self", [self.current_type.name])

        for method in self.current_type.methods:
            if method.return_type == AutoType():
                types = list(self.context.types.keys())
            else:
                types = [method.return_type.name]

            ty_bags.define_variable(method.name, types)

        for attr in self.current_type.attributes:
            if attr.type == AutoType():
                types = list(self.context.types.keys())
            else:
                types = [attr.type.name]
            ty_bags.define_variable(attr.name, types)

        for feat in node.feature_list:
            self.visit(feat, ty_bags)
        return ty_bags

    @visitor.when(AttrDecl)
    def visit(self, node, ty_bags):
        return

    @visitor.when(FuncDecl)
    def visit(self, node, ty_bags):
        self.current_method = self.current_type.get_method(node.id)
        method_ty_bags = ty_bags.create_child(node)

        for pname, ptype in zip(
            self.current_method.param_names, self.current_method.param_types
        ):
            if ptype == AutoType():
                method_ty_bags.define_variable(pname, list(self.context.types.keys()))
            else:
                method_ty_bags.define_variable(pname, [ptype.name])

        self.visit(node.body, method_ty_bags)

        self.current_method = None

    @visitor.when(Assign)
    def visit(self, node, ty_bags):
        return

    @visitor.when(Dispatch)
    def visit(self, node, ty_bags):
        return

    @visitor.when(StaticDispatch)
    def visit(self, node, ty_bags):
        return

    @visitor.when(LetIn)
    def visit(self, node, ty_bags):
        let_ty_bags = ty_bags.create_child(node)
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, _ in decl_list:
            typex = self.context.get_type(_type)

            if typex == AutoType():
                let_ty_bags.define_variable(idx, list(self.context.types.keys()))
            else:
                let_ty_bags.define_variable(idx, [typex.name])

        self.visit(exp, let_ty_bags)

    # TODO
    @visitor.when(Case)
    def visit(self, node, ty_bags):
        self.visit(node.exp, ty_bags)

        for idx, typex, case_exp in node.case_list:

            new_ty_bags = ty_bags.create_child(case_exp)

            typex = self.context.get_type(typex)

            if typex == AutoType():
                new_ty_bags.define_variable(idx, list(self.context.types.keys()))
            else:
                new_ty_bags.define_variable(idx, [typex.name])

            self.visit(case_exp, new_ty_bags)

    @visitor.when(Block)
    def visit(self, node, ty_bags):
        for exp in node.expr_list:
            self.visit(exp, ty_bags)

    @visitor.when(Not)
    def visit(self, node, ty_bags):
        self.visit(node.exp, ty_bags)

    # TODO
    @visitor.when(Tilde)
    def visit(self, node, ty_bags):
        return

    @visitor.when(IsVoid)
    def visit(self, node, ty_bags):
        self.visit(node.exp, ty_bags)

    @visitor.when(ParenthExp)
    def visit(self, node, ty_bags):
        self.visit(node.exp, ty_bags)

    def arith(self, node, ty_bags):

        self.visit(node.left, ty_bags)
        self.visit(node.right, ty_bags)

    @visitor.when(Plus)
    def visit(self, node, ty_bags):
        self.arith(node, ty_bags)

    @visitor.when(Minus)
    def visit(self, node, ty_bags):
        self.arith(node, ty_bags)

    @visitor.when(Div)
    def visit(self, node, ty_bags):
        self.arith(node, ty_bags)

    @visitor.when(Mult)
    def visit(self, node, ty_bags):
        self.arith(node, ty_bags)

    def comp(self, node, ty_bags):
        self.visit(node.left, ty_bags)
        self.visit(node.right, ty_bags)

    @visitor.when(Leq)
    def visit(self, node, ty_bags):
        self.comp(node, ty_bags)

    @visitor.when(Eq)
    def visit(self, node, ty_bags):
        self.comp(node, ty_bags)

    @visitor.when(Le)
    def visit(self, node, ty_bags):
        self.comp(node, ty_bags)

    @visitor.when(WhileLoop)
    def visit(self, node, ty_bags):
        pass
        self.visit(node.left, ty_bags)
        self.visit(node.right, ty_bags)

    @visitor.when(IfThenElse)
    def visit(self, node, ty_bags):
        self.visit(node.first, ty_bags)
        self.visit(node.second, ty_bags)
        self.visit(node.third, ty_bags)

    @visitor.when(StringExp)
    def visit(self, node, ty_bags):
        pass

    @visitor.when(BoolExp)
    def visit(self, node, ty_bags):
        pass

    @visitor.when(IntExp)
    def visit(self, node, ty_bags):
        pass

    @visitor.when(IdExp)
    def visit(self, node, ty_bags):
        pass

    @visitor.when(NewType)
    def visit(self, node, ty_bags):
        pass


class BagsReducer:
    def __init__(self, ty_bags, context, errors=[]):
        self.current_type = None
        self.current_method = None
        self.context = context
        self.errors = errors
        self.ty_bags = ty_bags

    @visitor.on("node")
    def visit(self, node, ty_bags, restriction):
        pass

    @visitor.when(Program)
    def visit(self, node, ty_bags=None, restriction=None):

        _ty_bags = TyBags()
        print(_ty_bags.compare(self.ty_bags))

        while not self.ty_bags.compare(_ty_bags):
            _ty_bags.clone(self.ty_bags)

            for cool_class in node.cool_class_list:
                self.visit(cool_class, self.ty_bags, [])
            self.ty_bags.clean()

        return self.ty_bags

    @visitor.when(CoolClass)
    def visit(self, node, ty_bags, restriction):
        self.current_type = self.context.get_type(node.id)
        ty_bags = ty_bags.children[node]

        for feat in node.feature_list:
            self.visit(feat, ty_bags, [])
        self.current_type = None

    @visitor.when(AttrDecl)
    def visit(self, node, ty_bags, restriction):
        if node.body is None:
            return
        else:
            ty_bags.reduce_bag(node, self.visit(node.body, ty_bags, []))

    @visitor.when(FuncDecl)
    def visit(self, node, ty_bags, restriction):
        pass
        self.current_method = self.current_type.get_method(node.id)
        method_ty_bags = ty_bags.children[node]

        return_types = self.visit(node.body, method_ty_bags, [])

        method_ty_bags.reduce_bag(node, return_types)

        self.current_method = None

    @visitor.when(Assign)
    def visit(self, node, ty_bags, restriction):
        types = self.visit(
            node.value,
            ty_bags,
            []
            if ty_bags.find_variable(node.id) is None
            else ty_bags.find_variable(node.id),
        )

        ty_bags.reduce_bag(node, types)
        return ty_bags.find_variable(node.id)

    # TODO fix dispatch. Find an elegant way to do it.
    @visitor.when(Dispatch)
    def visit(self, node, ty_bags, restriction):

        exp_type = self.context.types[list(self.visit(node.exp, ty_bags, []))[0]]

        for arg in node.exp_list:
            arg_types = self.visit(arg, ty_bags, [])
            ty_bags.reduce_bag(arg, arg_types)

        while ty_bags.parent is not None:
            ty_bags = ty_bags.parent

        for _, ty in ty_bags.children.items():

            if list(ty.vars["self"])[0] == exp_type.name:
                ty_bags = ty
                break

        return ty_bags.find_variable(node.id)

    # TODO
    @visitor.when(StaticDispatch)
    def visit(self, node, ty_bags, restriction):
        pass

    @visitor.when(LetIn)
    def visit(self, node, ty_bags, restriction):
        pass
        let_ty_bags = ty_bags.children[node]
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, expx in decl_list:
            # typex = self.context.get_type(_type)

            if expx is not None:
                ty_bags.reduce_bag(node, self.visit(expx, ty_bags, []))

        let_types = self.visit(exp, let_ty_bags, [])

        return let_types

    # TODO
    @visitor.when(Case)
    def visit(self, node, ty_bags, restriction):
        pass
        _ = self.visit(node.exp, ty_bags, [])
        return_types = []
        ances_type = None

        for idx, typex, case_exp in node.case_list:

            new_ty_bags = ty_bags.children[case_exp]

            typex = self.context.get_type(typex)

            static_types = self.visit(case_exp, new_ty_bags, [])

            if len(static_types) == 0:
                ances_type = lowest_common_ancestor(
                    ances_type, self.context.get_type[static_types[0]], self.context
                )

            else:
                return_types = set.union(set(return_types), set(static_types))

        return set.union(set(return_types), set([ances_type.name]))

    @visitor.when(Block)
    def visit(self, node, ty_bags, restriction):
        li = []
        for exp in node.expr_list[0 : len(node.expr_list) - 1]:
            exp_types = self.visit(exp, ty_bags, li)

        last = node.expr_list[len(node.expr_list) - 1]
        exp_types = self.visit(last, ty_bags, restriction)
        if len(restriction) > 0:
            ty_bags.reduce_bag(last, restriction)

        return exp_types

    @visitor.when(Not)
    def visit(self, node, ty_bags, restriction):
        _ = self.visit(node.exp, ty_bags, [])

        return set([BoolType().name])

    # TODO
    @visitor.when(Tilde)
    def visit(self, node, ty_bags, restriction):
        pass

    @visitor.when(IsVoid)
    def visit(self, node, ty_bags, restriction):
        _ = self.visit(node.exp, ty_bags, [])
        return set([BoolType().name])

    @visitor.when(ParenthExp)
    def visit(self, node, ty_bags, restriction):
        self.visit(node.exp, ty_bags, [])

    def arith(self, node, ty_bags):

        _ = self.visit(node.left, ty_bags, [IntType().name])
        _ = self.visit(node.right, ty_bags, [IntType().name])
        ty_bags.reduce_bag(node.left, [IntType().name])
        ty_bags.reduce_bag(node.right, [IntType().name])
        return set([IntType().name])

    @visitor.when(Plus)
    def visit(self, node, ty_bags, restriction):
        return self.arith(node, ty_bags)

    @visitor.when(Minus)
    def visit(self, node, ty_bags, restriction):
        return self.arith(node, ty_bags)

    @visitor.when(Div)
    def visit(self, node, ty_bags, restriction):
        return self.arith(node, ty_bags)

    @visitor.when(Mult)
    def visit(self, node, ty_bags, restriction):
        return self.arith(node, ty_bags)

    def comp(self, node, ty_bags):
        _ = self.visit(node.left, ty_bags, [])
        _ = self.visit(node.right, ty_bags, [])
        return set([BoolType().name])

    @visitor.when(Leq)
    def visit(self, node, ty_bags, restriction):
        return self.comp(node, ty_bags)

    @visitor.when(Eq)
    def visit(self, node, ty_bags, restriction):
        return self.comp(node, ty_bags)

    @visitor.when(Le)
    def visit(self, node, ty_bags, restriction):
        return self.comp(node, ty_bags)

    @visitor.when(WhileLoop)
    def visit(self, node, ty_bags, restriction):
        pass
        _ = self.visit(node.left, ty_bags, [BoolType().name])
        _ = self.visit(node.right, ty_bags, [])

        return set([self.context.get_type("Object").name])

    @visitor.when(IfThenElse)
    def visit(self, node, ty_bags, restriction):
        pass
        _ = self.visit(node.first, ty_bags, [BoolType().name])
        then_types = self.visit(node.second, ty_bags, [])
        else_types = self.visit(node.third, ty_bags, [])

        inters = then_types & else_types

        if len(inters) > 0:
            return inters

        return set.union(then_types, else_types)

    @visitor.when(StringExp)
    def visit(self, node, ty_bags, restriction):
        pass
        return set([StringType().name])

    @visitor.when(BoolExp)
    def visit(self, node, ty_bags, restriction):
        pass
        return set([BoolType().name])

    @visitor.when(IntExp)
    def visit(self, node, ty_bags, restriction):
        pass
        return set([IntType().name])

    @visitor.when(IdExp)
    def visit(self, node, ty_bags, restriction):
        return ty_bags.find_variable(node.id)

    @visitor.when(NewType)
    def visit(self, node, ty_bags, restriction):
        return set([node.type])
