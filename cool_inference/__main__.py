import sys
from lark import UnexpectedCharacters, UnexpectedToken
from cool_inference.parsing.parser import parser
from cool_inference.semantics.check import TypeCollector, TypeBuilder, TypeChecker


def pipeline(code):
    # parsing

    try:
        ast = parser.parse(code)
    except UnexpectedCharacters as e:
        print("Lexical error")
        print(e)
        print()
        print("Stopped because of lexical error")
        return
    except UnexpectedToken as e:
        print("Parsing error")
        print(e)
        print()
        print("Stopped because of parsing error")
        return

    print("Parsing finished without errors")
    print()

    # type collection

    type_collector_errors = []

    collector = TypeCollector(type_collector_errors)
    collector.visit(ast)

    if type_collector_errors:
        print("Type collector errors")
        for e in type_collector_errors:
            print(e)
    else:
        print("Type collector finished without errors")
    print()

    context = collector.context

    # type building

    type_builder_errors = []

    builder = TypeBuilder(context, type_builder_errors)
    builder.visit(ast)

    if type_builder_errors:
        print("Type builder errors")
        for e in type_builder_errors:
            print(e)
    else:
        print("Type builder finished without errors")
    print()

    # type checking

    type_checker_errors = []

    checker = TypeChecker(context, type_checker_errors)
    checker.visit(ast)

    if type_checker_errors:
        print("Type checker errors")
        for e in type_checker_errors:
            print(e)
    else:
        print("Type checker finished without errors")
    print()

    if type_collector_errors or type_builder_errors or type_checker_errors:
        print("Stopped because of semantic errors")
        return


def main():
    with open(sys.argv[1]) as fp:
        code = fp.read()
    pipeline(code)


if __name__ == "__main__":
    main()
