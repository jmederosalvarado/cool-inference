from cool_inference.parsing.parser import parser
from cool_inference.semantics.check import TypeCollector, TypeBuilder, TypeChecker
from cool_inference.inference.tyinfer import BagsCollector, BagsReducer
from cool_inference.utils.utils import search_for_errors


def test13():
    test13 = """
        class A {

            f ( x : AUTO_TYPE ) : AUTO_TYPE {
                    x
            } ;

            g ( x : AUTO_TYPE ) : AUTO_TYPE {
                    f(x+1)
            } ;

            h ( x : String ) : AUTO_TYPE {
                    f(x)
            } ;

        } ;


            """

    ast = parser.parse(test13)

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

    search_for_errors(bags, errors)

    print("Errors: [")
    for error in errors:
        print("\t", error)
    print("]")

    assert errors == [
        "Can't infer type of: 'f', between['Int', 'String']",
        "Can't infer type of: 'g', between['Int', 'String']",
        "Can't infer type of: 'h', between['Int', 'String']",
        "Can't infer type of: 'x', between['Int', 'String']",
    ]
