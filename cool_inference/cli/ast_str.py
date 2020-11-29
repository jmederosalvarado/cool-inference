import cool_inference.utils.visitor as visitor
from cool_inference.ast import (
    Assign,
    AttrDecl,
    Block,
    BoolExp,
    Case,
    CoolClass,
    Dispatch,
    Div,
    Eq,
    FuncDecl,
    IdExp,
    IfThenElse,
    IntExp,
    IsVoid,
    Le,
    Leq,
    LetIn,
    Minus,
    Mult,
    NewType,
    Not,
    Param,
    ParenthExp,
    Plus,
    Program,
    StaticDispatch,
    StringExp,
    Tilde,
    WhileLoop,
)


class AstStr(object):
    @visitor.on("node")
    def visit(self, node, indent):
        pass

    @visitor.when(Assign)
    def visit(self, node: Assign, indent):  # noqa: F811
        return "{id} <- {exp}".format(id=node.id, exp=node.value)

    @visitor.when(AttrDecl)
    def visit(self, node: AttrDecl, indent):  # noqa: F811
        decl = "{id}: {type}".format(id=node.id, type=node.type)
        init = (
            "<- {value}".format(value=self.visit(node.body, indent))
            if node.body
            else ""
        )
        return decl + init

    @visitor.when(Block)
    def visit(self, node: Block, indent):  # noqa: F811
        expr_list = (self.visit(exp, indent + 1) for exp in node.expr_list)
        expr_list = ("  " * (indent + 1) + exp for exp in expr_list)
        body = "\n".join(expr_list)
        return "{{\n{body}\n{indent}}}".format(body=body, indent="  " * indent)

    @visitor.when(BoolExp)
    def visit(self, node: BoolExp, indent):  # noqa: F811
        return node.lex

    @visitor.when(Case)
    def visit(self, node: Case, indent):  # noqa: F811
        cases = (
            (idx, typex, self.visit(exp, indent + 1))
            for (idx, typex, exp) in node.case_list
        )
        cases = (
            "{id}: {type} => {exp}".format(id=idx, type=typex, exp=exp)
            for (idx, typex, exp) in cases
        )
        cases = ("  " * (indent + 1) + case for case in cases)
        cases = "\n".join(cases)
        return "case {exp} of\n{cases}\n{indent}esac".format(
            exp=self.visit(node.exp, indent), cases=cases, indent="  " * indent
        )

    @visitor.when(CoolClass)
    def visit(self, node: CoolClass, indent):  # noqa: F811
        decl = "{id} inherits {parent}".format(id=node.id, parent=node.inherit)
        features = (self.visit(feat, indent + 1) for feat in node.feature_list)
        features = ("  " * (indent + 1) + feat for feat in features)
        features = "\n".join(features)
        return "{decl} {{\n{feats}\n{indent}}}\n".format(
            decl=decl, feats=features, indent="  " * indent
        )

    @visitor.when(Dispatch)
    def visit(self, node: Dispatch, indent):  # noqa: F811
        arg_list = ", ".join((self.visit(exp, indent) for exp in node.exp_list))
        exp = "{exp}.".format(exp=self.visit(node.exp, indent)) if node.exp else ""
        return exp + "{id}({arg_list})".format(id=node.id, arg_list=arg_list)

    @visitor.when(Div)
    def visit(self, node: Div, indent):  # noqa: F811
        return "{left} / {right}".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )

    @visitor.when(Eq)
    def visit(self, node: Eq, indent):  # noqa: F811
        return "{left} = {right}".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )

    @visitor.when(FuncDecl)
    def visit(self, node: FuncDecl, indent):  # noqa: F811
        params = ", ".join((self.visit(p, indent) for p in node.params))
        body = "  " * (indent + 1) + self.visit(node.body, indent + 1)
        return "{id}({params}): {type} {{\n{body}\n{indent}}}".format(
            id=node.id,
            params=params,
            type=node.type,
            body=body,
            indent="  " * indent,
        )

    @visitor.when(IdExp)
    def visit(self, node: IdExp, indent):  # noqa: F811
        return node.id

    @visitor.when(IfThenElse)
    def visit(self, node: IfThenElse, indent):  # noqa: F811
        cond = self.visit(node.first, indent)
        then_exp = self.visit(node.second, indent)
        else_exp = self.visit(node.third, indent)
        return "if {cond} then {then_exp} else {else_exp} fi".format(
            cond=cond, then_exp=then_exp, else_exp=else_exp
        )

    @visitor.when(IntExp)
    def visit(self, node: IntExp, indent):  # noqa: F811
        return node.lex

    @visitor.when(IsVoid)
    def visit(self, node: IsVoid, indent):  # noqa: F811
        return "isvoid {exp}".format(exp=self.visit(node.exp, indent))

    @visitor.when(Le)
    def visit(self, node: Le, indent):  # noqa: F811
        return "{left} < {right}".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )

    @visitor.when(Leq)
    def visit(self, node: Leq, indent):  # noqa: F811
        return "{left} <= {right}".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )

    @visitor.when(LetIn)
    def visit(self, node: LetIn, indent):  # noqa: F811
        decls = ", ".join((self.visit(decl, indent) for decl in node.decl_list))
        expr = self.visit(node.exp, indent)
        return "let {decls} in {expr}".format(decls=decls, expr=expr)

    @visitor.when(Minus)
    def visit(self, node: Minus, indent):  # noqa: F811
        return "{left} - {right}".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )

    @visitor.when(Mult)
    def visit(self, node: Mult, indent):  # noqa: F811
        return "{left} * {right}".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )

    @visitor.when(NewType)
    def visit(self, node: NewType, indent):  # noqa: F811
        return "new {type}".format(type=node.type)

    @visitor.when(Not)
    def visit(self, node: Not, indent):  # noqa: F811
        return "not {exp}".format(exp=self.visit(node.exp, indent))

    @visitor.when(Param)
    def visit(self, node: Param, indent):  # noqa: F811
        return "{id}: {type}".format(id=node.id, type=node.type)

    @visitor.when(ParenthExp)
    def visit(self, node: ParenthExp, indent):  # noqa: F811
        return "({exp})".format(exp=self.visit(node.exp, indent))

    @visitor.when(Plus)
    def visit(self, node: Plus, indent):  # noqa: F811
        return "{left} + {right}".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )

    @visitor.when(Program)
    def visit(self, node: Program, indent):  # noqa: F811
        return "\n".join((self.visit(cl, indent) for cl in node.cool_class_list))

    @visitor.when(StaticDispatch)
    def visit(self, node: StaticDispatch, indent):  # noqa: F811
        arg_list = ", ".join((self.visit(exp, indent) for exp in node.exp_list))
        exp = self.visit(node.exp, indent)
        return "{exp}@{type}.{id}({arg_list})".format(
            exp=exp, type=node.specific_type, id=node.id, arg_list=arg_list
        )

    @visitor.when(StringExp)
    def visit(self, node: StringExp, indent):  # noqa: F811
        return node.lex

    @visitor.when(Tilde)
    def visit(self, node: Tilde, indent):  # noqa: F811
        return "~{exp}".format(exp=self.visit(node.exp, indent))

    @visitor.when(WhileLoop)
    def visit(self, node: WhileLoop, indent):  # noqa: F811
        return "while {left} loop {right} pool".format(
            left=self.visit(node.left, indent), right=self.visit(node.right, indent)
        )
