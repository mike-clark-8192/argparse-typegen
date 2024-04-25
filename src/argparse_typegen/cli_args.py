import argparse


class ArgsNamespace:
    getter: str
    path: list[str]
    generate_argcheck: bool

    def __setattr__(self, name_, value_) -> None:
        import types, typing

        hints = typing.get_type_hints(self)
        if name_ not in hints:
            raise ValueError(f"{name_} is not a declared attribute of {type(self)}")
        decltype = hints[name_]
        if isinstance(decltype, types.GenericAlias):
            decltype = decltype.__origin__
        valtype = type(value_)
        if value_ is not None and not issubclass(valtype, decltype):
            raise ValueError(
                f"Declared type '{decltype.__name__}' of attribute '{name_}'"
                f" is incompatible with value type '{valtype.__name__}', value={value_}"
            )
        super().__setattr__(name_, value_)


def build_argparser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-g",
        "--getter",
        type=str,
        required=True,
        help="Python statement to retrieve the argparse.ArgumentParser instance.\n"
        "    Example 1: mymodule.get_parser() # call a function\n"
        "    Example 2: mymodule.parser       # get an attribute",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        nargs="+",
        required=False,
        help="Paths to append to module search path (sys.path).\n    Example: ./src",
    )
    parser.add_argument(
        "-c",
        "--generate-argcheck",
        action="store_true",
        help="Generate an __setattr__ method to check attribute types at runtime.",
    )
    return parser
