import sys
from lark import UnexpectedCharacters, UnexpectedToken
from cool_inference.parsing.parser import parser
from cool_inference.semantics.check import TypeCollector, TypeBuilder, TypeChecker


def get_rich_printers():
    from rich import print

    def print_title(title):
        styled = f":point_right: [bold cyan]{title}[/]"
        print(styled)

    def print_error(error):
        styled = f":cry: [red]{error}[/]"
        print(styled)

    def print_success(success):
        styled = f":smiley: [green]{success}[/]"
        print(styled)

    def print_exit(exit_):
        styled = f":x: [bold red]{exit_}[/]"
        print(styled)

    return print_title, print_error, print_success, print_exit


def get_std_printers():
    def print_title(title):
        print(f"---------> {title}")

    def print_error(error):
        print(f"[error] {error}")

    def print_success(success):
        print(f"[success] {success}")

    def print_exit(exit_):
        print(f"---------> {exit_}")

    def print_ast(exit_):
        print(f"---------> {exit_}")

    return print_title, print_error, print_success, print_exit


def pipeline(code):
    try:
        printers = get_rich_printers()
    except ImportError:
        printers = get_std_printers()

    print_title, print_error, print_success, print_exit = printers

    # parsing

    print_title("Tokenizing/Parsing")

    try:
        ast = parser.parse(code)
    except UnexpectedCharacters as e:
        print_error(
            f"Unexpected character {code[e.pos_in_stream]} at ({e.line}, {e.column})"
        )
        print()
        print_exit("Stopped because of lexical error")
        return
    except UnexpectedToken as e:
        print_error(f"Unexpected token {e.token} at ({e.line}, {e.column})")
        print()
        print_exit("Stopped because of parsing error")
        return

    print_success("Finished without errors")
    print()

    # type collection

    print_title("Type collection")

    type_collector_errors = []

    collector = TypeCollector(type_collector_errors)
    collector.visit(ast)

    if type_collector_errors:
        for e in type_collector_errors:
            print_error(e)
    else:
        print_success("Finished without errors")
    print()

    context = collector.context

    # type building

    print_title("Type building")

    type_builder_errors = []

    builder = TypeBuilder(context, type_builder_errors)
    builder.visit(ast)

    if type_builder_errors:
        for e in type_builder_errors:
            print_error(e)
    else:
        print_success("Finished without errors")
    print()

    # type checking

    print_title("Type checking")

    type_checker_errors = []

    checker = TypeChecker(context, type_checker_errors)
    checker.visit(ast)

    if type_checker_errors:
        for e in type_checker_errors:
            print_error(e)
    else:
        print_success("Finished without errors")
    print()

    if type_collector_errors or type_builder_errors or type_checker_errors:
        print_exit("Stopped because of semantic errors")
        return


def main():
    with open(sys.argv[1]) as fp:
        code = fp.read()
    pipeline(code)


if __name__ == "__main__":
    main()
