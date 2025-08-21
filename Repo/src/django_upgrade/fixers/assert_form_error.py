"""
Update calls to assertFormError() / assertFormSetError() to pass the
form/formset instead of the response.

https://docs.djangoproject.com/en/4.1/releases/4.1/#tests
"""
from __future__ import annotations

import ast
from functools import partial
from typing import Iterable

from tokenize_rt import Offset, Token

from django_upgrade.ast import ast_start_offset
from django_upgrade.data import Fixer, State, TokenFunc
from django_upgrade.tokens import (
    OP,
    UNIMPORTANT_WS,
    find,
    find_first_token,
)

fixer = Fixer(
    __name__,
    min_version=(4, 1),
)


@fixer.register(ast.Call)
def visit_Call(
    state: State,
    node: ast.Call,
    parent: ast.AST,
) -> Iterable[tuple[Offset, TokenFunc]]:
    if (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "assertFormError"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
        and len(node.args) in (4, 5)
        and len(node.keywords) == 0
        and isinstance(node.args[0], ast.Name)
        and (
            isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
            or isinstance(node.args[1], ast.Name)
        )
    ):
        yield ast_start_offset(node.args[0]), partial(
            rewrite_args,
            response_arg=node.args[0],
            form_arg=node.args[1],
        )


def rewrite_args(
    tokens: list[Token],
    i: int,
    *,
    response_arg: ast.Name,
    form_arg: ast.Constant | ast.Name,
) -> None:
    # Find the response token
    response_idx = find_first_token(tokens, i, node=response_arg)

    # Find the form token
    form_idx = find_first_token(tokens, response_idx + 1, node=form_arg)

    # Get the form value
    form_str = tokens[form_idx].src

    # Replace the response token with response.context[form]
    tokens[response_idx] = tokens[response_idx]._replace(
        src=tokens[response_idx].src + ".context[" + form_str + "]"
    )

    # Find the comma after response
    comma_idx = response_idx + 1
    while comma_idx < len(tokens) and tokens[comma_idx].src != ",":
        comma_idx += 1

    # Find the token after form (should be a comma)
    after_form_idx = form_idx + 1
    while after_form_idx < len(tokens) and tokens[after_form_idx].name == UNIMPORTANT_WS:
        after_form_idx += 1

    # Delete from the comma after response up to (but not including) the comma after form
    del tokens[comma_idx:after_form_idx]
