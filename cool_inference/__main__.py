import sys
from lark import UnexpectedCharacters, UnexpectedToken
from cool_inference.parsing.parser import parser
from cool_inference.semantics.check import TypeCollector


def pipeline(code):
    try:
        ast = parser.parse(code)
    except UnexpectedCharacters as e:
        print(e)
        return
    except UnexpectedToken as e:
        print(e)
        return

    type_collector_errors = []

    collector = TypeCollector(type_collector_errors)
    collector.visit(ast)


def main():
    with open(sys.argv[1]) as fp:
        code = fp.read()
    pipeline(code)


if __name__ == "__main__":
    main()
