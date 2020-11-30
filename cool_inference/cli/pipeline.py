from lark import UnexpectedCharacters, UnexpectedToken
from cool_inference.parsing.parser import parser
from cool_inference.semantics.check import TypeCollector, TypeBuilder, TypeChecker
from cool_inference.inference.tyinfer import BagsCollector, BagsReducer, BagsReplacer
from cool_inference.cli.ast_str import AstStr


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

    # bags collection

    print_title("Collecting tybags")

    bags_collector_errors = []

    bags_collector = BagsCollector(context, bags_collector_errors)
    bags = bags_collector.visit(ast)

    if bags_collector_errors:
        for e in bags_collector_errors:
            print_error(e)
    else:
        print_success("Finished without errors")
    print()

    # bags reducing

    print_title("Reducing tybags")

    bags_reducer_errors = []

    bags_reducer = BagsReducer(bags, context, bags_reducer_errors)
    bags = bags_reducer.visit(ast)

    if bags_reducer_errors:
        for e in bags_reducer_errors:
            print_error(e)
    else:
        print_success("Finished without errors")
    print()

    # bags replacing

    print_title("Replacing tybags in ast")

    bags_replacer_errors = []

    bags_replacer = BagsReplacer(bags, context, bags_replacer_errors)
    bags_replacer.visit(ast)

    if bags_replacer_errors:
        for e in bags_replacer_errors:
            print_error(e)
    else:
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

    ast_str = AstStr()
    return ast_str.visit(ast, 0)
