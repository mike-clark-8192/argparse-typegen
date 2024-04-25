import argparse
import sys
from . import execeval
from . import typegen
from . import cli_args


def main(argv=sys.argv[1:]):
    parser = cli_args.build_argparser()
    args = parser.parse_args(argv, namespace=cli_args.ArgsNamespace())
    if args.path:
        sys.path.extend(args.path)
    getter = args.getter
    their_parser = execeval.execeval(getter)
    if not isinstance(their_parser, argparse.ArgumentParser):
        raise TypeError(f"{getter} did not return an argparse.ArgumentParser instance.")
    result = typegen.generate_argparse_namespace_code(
        their_parser, generate_argcheck=args.generate_argcheck
    )
    print(result)


if __name__ == "__main__":
    main()
