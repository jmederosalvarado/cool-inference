from cool_inference.parsing.parser import parser
from cool_inference.semantics.check import TypeCollector, TypeBuilder, TypeChecker
from cool_inference.inference.tyinfer import BagsCollector, BagsReducer, BagsReplacer


def test6():
    test6 = """
        class A {
            step(p : AUTO_TYPE) : AUTO_TYPE { p.translate(1,1) } ;

            main() : Object {
                let p : AUTO_TYPE in
                    step(p)
            } ;
        } ;

        class Point {
            translate ( a : Int, b:Int ) : Int {
                a + b
            } ;
        } ;
            """

    ast = parser.parse(test6)

    errors = []

    collector = TypeCollector(errors)
    collector.visit(ast)

    context = collector.context

    print("================= TYPE COLLECTOR =================")
    print("Errors:", errors)
    print("Context:")
    print(context)
    print("")

    print("================= TYPE BUILDER =================")
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    print("Errors: [")
    for error in errors:
        print("\t", error)
    print("]")
    print("Context:")
    print(context)

    print("=============== CHECKING TYPES ================")
    checker = TypeChecker(context, errors)
    _ = checker.visit(ast)
    print("Errors: [")
    for error in errors:
        print("\t", error)
    print("]")

    if errors != []:
        assert False

    errors = []

    print("================= BAGS COLLECTOR =================")
    collector = BagsCollector(context, errors)

    bags = collector.visit(ast)
    print("LIST:")
    print(bags)
    print("")

    print("================= BAGS REDUCER =================")
    collector = BagsReducer(bags, context, errors)

    bags = collector.visit(ast)
    print("LIST:")
    print(bags)
    print("")

    print("Errors: [")
    for error in errors:
        print("\t", error)
    print("]")

    errors = []

    print("================= BAGS REPLACER=================")
    replacer = BagsReplacer(bags, context, errors)
    replacer.visit(ast)

    print("================= TYPE COLLECTOR =================")
    errors = []

    collector = TypeCollector(errors)
    collector.visit(ast)

    context = collector.context
    print("Errors:", errors)
    print("Context:")
    print(context)
    print("")

    print("================= TYPE BUILDER =================")
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    print("Errors: [")
    for error in errors:
        print("\t", error)
    print("]")
    print("Context:")
    print(context)

    print("=============== CHECKING TYPES ================")
    checker = TypeChecker(context, errors)
    _ = checker.visit(ast)
    print("Errors: [")
    for error in errors:
        print("\t", error)
    print("]")

    assert errors == []
