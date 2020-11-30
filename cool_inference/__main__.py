import sys
import os
from cool_inference.cli.pipeline import pipeline


def main():
    filename = sys.argv[1]
    with open(filename) as fp:
        code = fp.read()
    ast_str = pipeline(code)

    if ast_str is None:
        return

    basename, extension = os.path.splitext(filename)
    with open(basename + "-inferred" + extension, "w") as fp:
        fp.write(ast_str)


if __name__ == "__main__":
    main()
