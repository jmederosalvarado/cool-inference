import sys
from cool_inference.cli.pipeline import pipeline


def main():
    with open(sys.argv[1]) as fp:
        code = fp.read()
    pipeline(code)


if __name__ == "__main__":
    main()
