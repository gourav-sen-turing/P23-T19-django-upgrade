"""
Update calls to assertFormError() / assertFormSetError() to pass the
form/formset instead of the response.

https://docs.djangoproject.com/en/4.1/releases/4.1/#tests
"""
from __future__ import annotations

import ast
from functools import partial
from typing import Iterable

from tokenize_rt import UNIMPORTANT_WS, Offset, Token, tokens_to_src

from django_upgrade.ast import ast_start_offset
from django_upgrade.data import Fixer, State, TokenFunc
from django_upgrade.tokens import (
    OP,
    PHYSICAL_NEWLINE,
    consume,
    find_final_token,
    find_first_token,
    reverse_consume,
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
        and isinstance((first_arg := node.args[0]), ast.Name)
        and (
            isinstance((second_arg := node.args[1]), ast.Constant)
            and isinstance(second_arg.value, (str, int))
            or isinstance(second_arg, ast.Name)
        )
    ):
        yield ast_start_offset(first_arg), partial(
            rewrite_args,
            response_arg=first_arg,
            form_arg=second_arg,
        )


def rewrite_args(
    tokens: list[Token],
    i: int,
    *,
    response_arg: ast.Name,
    form_arg: ast.Constant | ast.Name,
) -> None:
    # Get the form name to embed in the context access
    form_start = find_first_token(tokens, i, node=form_arg)
    form_end = find_final_token(tokens, form_start, node=form_arg)
    form_tokens = tokens[form_start:form_end]
    form_src = tokens_to_src(form_tokens)

    # Find the comma after the response argument
    response_comma = i + 1
    while response_comma < len(tokens) and tokens[response_comma].src != ",":
        response_comma += 1

    # We need to delete:
    # - comma after response
    # - any whitespace
    # - the form argument
    # But keep the comma after the form
    delete_start = response_comma
    delete_end = form_end

    # Handle multiline case - if there's a newline between response comma and form,
    # include any whitespace before the form in the deletion
    has_newline = False
    for idx in range(response_comma + 1, form_start):
        if tokens[idx].name == PHYSICAL_NEWLINE:
            has_newline = True
            break

    if has_newline:
        # Find and include whitespace before the form
        while delete_start > 0 and tokens[delete_start - 1].name == UNIMPORTANT_WS:
            delete_start -= 1

    # Perform the deletion
    del tokens[delete_start:delete_end]

    # Replace the response token
    response_token = tokens[i]
    tokens[i] = response_token._replace(
        src=response_token.src + ".context[" + form_src + "]"
    )
