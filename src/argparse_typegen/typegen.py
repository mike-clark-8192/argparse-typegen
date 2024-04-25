import argparse
import typing
import os
import types
import textwrap


def get_type_fqtn(typ: typing.Type):
    if not isinstance(typ, type):
        return "any"
    module = typ.__module__
    if module == int.__module__ or module.startswith("__"):
        module = ""
    else:
        module += "."
    return module + typ.__qualname__


def get_argparse_fqtn(tc: typing.Any):
    if tc is None:
        return "str"
    if isinstance(tc, type):
        module_prefix = get_module_prefix(tc)
        return f"{module_prefix}{tc.__name__}"
    elif isinstance(tc, types.GenericAlias):
        # Handling for generic types like list[str] or dict[str, int]
        base = tc.__origin__.__name__
        args = ", ".join([get_argparse_fqtn(arg) for arg in tc.__args__])
        module_prefix = get_module_prefix(tc)
        return f"{module_prefix}{base}[{args}]"
    elif isinstance(tc, argparse.FileType):
        with tc(os.devnull) as ft:
            return get_type_fqtn(type(ft)).replace("_io.", "io.")
    elif callable(tc):
        hints = typing.get_type_hints(tc)
        if hints and "return" in hints:
            return get_type_fqtn(hints["return"])
        if hasattr(tc, "__call__"):
            hints = typing.get_type_hints(tc.__call__)
            if hints and "return" in hints:
                return get_type_fqtn(hints["return"])
    return get_type_fqtn(tc)


def get_module_prefix(tc):
    if hasattr(tc, "__origin__"):
        origin: typing.Type = tc.__origin__
        module = origin.__module__
    else:
        module = tc.__module__
    if module == "builtins":
        module_prefix = ""
    else:
        module_prefix = f"{module}."
    return module_prefix


def get_attrcheck_method_code(indent=" " * 4):
    fnsig = "def __setattr__(self, name_: str, value_: typing.Any) -> None:"
    fnbody = textwrap.dedent(
        """\
    import typing
    hints = typing.get_type_hints(self)
    if name_ not in hints:
        raise ValueError(f"{name_} is not a declared attribute of {type(self)}")
    decltype = hints[name_]
    if isinstance(decltype, types.GenericAlias):
        decltype = decltype.__origin__
    valtype = type(value_)
    if value_ is not None and not issubclass(valtype, decltype):
        raise ValueError(f"Declared type '{decltype.__name__}' of attribute '{name_}'"
                            f" is incompatible with value type '{valtype.__name__}', value={value_}")
    super().__setattr__(name_, value_)
    """
    )
    fnbody = textwrap.indent(fnbody, indent)
    return f"{fnsig}\n{fnbody}"


def generate_argparse_namespace_code(
    parser: argparse.ArgumentParser,
    indent=" " * 4,
    classname="ArgsNamespace",
    extra: dict[str, typing.Union[typing.Type, typing.Callable]] = {},
    generate_argcheck=False,
):
    action2code = generate_action2code(parser)
    code_lines = [f"class {classname}:"]
    code_lines[1:] = [f"{indent}{code}" for _, code in action2code.items()]
    for dest, type_or_callable in extra.items():
        qtn = get_argparse_fqtn(type_or_callable)
        code_lines.append(f"{indent}{dest}: {qtn}")
    if generate_argcheck:
        attrcheck_method_code = get_attrcheck_method_code(indent)
        attrcheck_method_code = textwrap.indent(attrcheck_method_code, indent)
        code_lines.append("")
        code_lines.append(attrcheck_method_code)
    code = "\n".join(code_lines)
    return code


def generate_action2code(parser):
    action2code: dict[argparse.Action, str] = {}
    for action in parser._actions:
        if action.default == argparse.SUPPRESS:
            continue
        if isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
            qtn = "bool"
        elif isinstance(action, argparse._CountAction):
            qtn = "int"
        else:
            qtn = get_argparse_fqtn(action.type)
        islist = isinstance(
            action, (argparse._AppendAction, argparse._AppendConstAction)
        )
        islist = islist or (isinstance(action.nargs, int) and action.nargs > 1)
        islist = islist or action.nargs == "*" or action.nargs == "+"
        if islist:
            qtn = f"list[{qtn}]"
        action2code[action] = f"{action.dest}: {qtn}"
    return action2code
