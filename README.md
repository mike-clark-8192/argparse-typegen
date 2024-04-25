# argparse-typegen

`argparse-typegen` is a Python CLI tool and library that generates a typed namespaces class from an argparse.ArgumentParser definition.
The generated class has no runtime dependencies.
Having a typed namespace class is primarily useful for getting IDE autocompletion for argparse-based scripts.

## Features

- **Type Inference**: Automatically generates types for argparse based on the provided parser definitions.
- **Support for Complex Types**: Handles complex types like lists, dictionaries, and custom `type=` arguments.
- **Easy to Use**: Simply provide a Python expression or statement that yields an `argparse.ArgumentParser` instance.

## Installation

An easy way to get up and running quickly is to use `pipx`:

```bash
pipx install <this-repo-url>
```

This should make the command `argparse-typegen` available in your shell.

## Basic usage example

To use `argparse-typegen`, you need to provide a Python expression or statement that yields an `argparse.ArgumentParser` instance.
Suppose your project `myproject` has the following `get_parser` function in the module `mymodule.cli`:

```python
# File: myproject/mymodule/cli.py
import argparse

def get_parser():
    parser = argparse.ArgumentParser(description='Sample parser')
    parser.add_argument('--count', type=int, help='Count')
    parser.add_argument('--names', nargs='+', help='Names')
    return parser
```

You can generate a typed namespace using:

```bash
cd myproject
argparse-typegen --getter "import mymodule.cli as cli; cli.get_parser()"
```

argparse-typegen will output the following namespace class:
```python
class ArgsNamespace:
    count: int
    names: list[str]
```

You can then paste this class into your project and use it in your scripts:

```python
args = get_parser().parse_args(namespace=ArgsNamespace())
# args should now be type-hinted as ArgsNamespace by IDEs
```

## Limitations

Contributions are welcome to improve the tool and add new features. Here are some limitations of the current version:

* Does not support option groups
* Does not support subparsers
* Does not support custom action classes

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the tool or add new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
