# TODO
# from cool_inference.parsing.parser import parser
# from cool_inference.semantics.check import TypeCollector, TypeBuilder, TypeChecker


# def test7():
#     test7 = """
#     class Silly {
#         copy() : SELF_TYPE { self };
#         };

#     class Sally inherits Silly { };

#     class Main {
#         x : Sally <- (new Sally).copy();
#         main() : Sally { x };
#     };
#         """

#     ast = parser.parse(test7)

#     errors = []

#     collector = TypeCollector(errors)
#     collector.visit(ast)

#     context = collector.context

#     print("================= TYPE COLLECTOR =================")
#     print("Errors:", errors)
#     print("Context:")
#     print(context)
#     print("")

#     print("================= TYPE BUILDER =================")
#     builder = TypeBuilder(context, errors)
#     builder.visit(ast)
#     print("Errors: [")
#     for error in errors:
#         print("\t", error)
#     print("]")
#     print("Context:")
#     print(context)

#     print("=============== CHECKING TYPES ================")
#     checker = TypeChecker(context, errors)
#     scope = None
#     _ = checker.visit(ast, scope)
#     print("Errors: [")
#     for error in errors:
#         print("\t", error)
#     print("]")

#     assert errors == []
