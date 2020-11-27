from cool_inference.parsing.parser import parser
from cool_inference.semantics.check import TypeCollector, TypeBuilder, TypeChecker
from cool_inference.inference.tyinfer import BagsCollector, BagsReducer
from cool_inference.utils.utils import search_for_errors


def test4():
    test4 = """
        class A {
            d : AUTO_TYPE ;
            a : AUTO_TYPE ;
            b : AUTO_TYPE ;
            c : AUTO_TYPE ;
            e : AUTO_TYPE ;
            f : AUTO_TYPE ;

            met1 ( ) : AUTO_TYPE {
                {
                    a <- b ;
                    b <- c ;
                    c <- d ;
                    d <- e + f ;
                    f <- "asd" ;
                    d <- true ;
                } + 5
            } ;
        } ;
            """

    ast = parser.parse(test4)

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
        "Can't infer type of: 'd', between['Bool', 'Int']",
        "Can't infer type of: 'a', between['Bool', 'Int']",
        "Can't infer type of: 'b', between['Bool', 'Int']",
        "Can't infer type of: 'c', between['Bool', 'Int']",
        "Can't infer type of: 'f', between['Int', 'String']",
    ]
