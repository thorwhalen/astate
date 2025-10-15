"""Extaction tools."""

from typing import Union, Optional, Tuple
from collections.abc import Iterable

import ast


def remove_decorator_code(
    src: str, decorator_names: str | Iterable[str] | None = None
) -> str:
    """
    Remove the code corresponding to decorators from a source code string.
    If decorator_names is None, will remove all decorators.
    If decorator_names is an iterable of strings, will remove the decorators with those names.

    Examples:
    >>> src = '''
    ... @decorator
    ... def func():
    ...     pass
    ... '''
    >>> print(remove_decorator_code(src))
    def func():
        pass

    >>> src = '''
    ... @decorator1
    ... @decorator2
    ... def func():
    ...     pass
    ... '''
    >>> print(remove_decorator_code(src, "decorator1"))
    @decorator2
    def func():
        pass
    """

    if isinstance(decorator_names, str):
        decorator_names = [decorator_names]

    class DecoratorRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.decorator_list:
                if decorator_names is None:
                    node.decorator_list = []  # Remove all decorators
                else:
                    node.decorator_list = [
                        d
                        for d in node.decorator_list
                        if not (isinstance(d, ast.Name) and d.id in decorator_names)
                    ]
            return node

        def visit_ClassDef(self, node):
            if node.decorator_list:
                if decorator_names is None:
                    node.decorator_list = []  # Remove all decorators
                else:
                    node.decorator_list = [
                        d
                        for d in node.decorator_list
                        if not (isinstance(d, ast.Name) and d.id in decorator_names)
                    ]
            return node

    tree = ast.parse(src)
    new_tree = DecoratorRemover().visit(tree)
    ast.fix_missing_locations(new_tree)

    return ast.unparse(new_tree)


def separate_decorator_code(
    src: str, decorator_names: str | Iterable[str] | None = None
) -> tuple[str, str]:
    """
    Separate decorator code and the main function/class code with decorators removed.

    Returns a tuple where the first element is the extracted decorator code, and the second
    element is the source code with decorators removed.

    Examples:
    >>> src = '''
    ... @decorator
    ... def func():
    ...     pass
    ... '''
    >>> decorators, code = separate_decorator_code(src)
    >>> print(decorators)
    @decorator

    >>> print(code)
    def func():
        pass
    """
    if isinstance(decorator_names, str):
        decorator_names = [decorator_names]

    class DecoratorExtractor(ast.NodeTransformer):
        extracted_decorators = []

        def visit_FunctionDef(self, node):
            if node.decorator_list:
                self.extracted_decorators.extend(node.decorator_list)
                node.decorator_list = []  # Remove decorators
            return node

        def visit_ClassDef(self, node):
            if node.decorator_list:
                self.extracted_decorators.extend(node.decorator_list)
                node.decorator_list = []  # Remove decorators
            return node

    tree = ast.parse(src)
    extractor = DecoratorExtractor()
    new_tree = extractor.visit(tree)
    ast.fix_missing_locations(new_tree)

    decorator_code = "\n".join(
        [f"@{ast.unparse(d)}" for d in extractor.extracted_decorators]
    )
    modified_code = ast.unparse(new_tree)

    return decorator_code, modified_code
