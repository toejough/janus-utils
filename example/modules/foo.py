def no_args():
    print("foo: no args!")


def positionals(first, second, third):
    print(
        "foo positionals:"
        f"\n  first: {first}"
        f"\n  second: {second}"
        f"\n  third: {third}"
    )


def variable_args(*args):
    print(
        "foo variable args:"
    )
    for each_arg in args:
        print(f"  {each_arg}")


def defaults(first='default 1', second='default 2', third='default 3'):
    print(
        "foo defaults:"
        f"\n  first: {first}"
        f"\n  second: {second}"
        f"\n  third: {third}"
    )


def keyword_args(*, first, second, third):
    print(
        "foo keyword args:"
        f"\n  first: {first}"
        f"\n  second: {second}"
        f"\n  third: {third}"
    )


def default_keyword_args(*, first='default 1', second='default 2', third='default 3'):
    print(
        "foo default keyword args:"
        f"\n  first: {first}"
        f"\n  second: {second}"
        f"\n  third: {third}"
    )


def variable_keyword_args(**kwargs):
    print(
        "foo variable keyword args:"
    )
    for name, arg in kwargs.items():
        print(f"  {name}: {arg}")


def docstring():
    """
    This function has a docstring.

    Multi-lined, but this shouldn't show up.
    """
    print("foo docstring!")


def typed(first: int):
    print(f"foo typed: {first}")


def combo(first: int, second: float=2.4, *args, third: str, fourth="default 3", **kwargs) -> None:
    """
    Combo docstring.

    Multi-lined, but this shouldn't show up.
    """
    print(
        "foo combo:"
        f"\n  first: {first}"
        f"\n  second: {second}"
    )
    for each_arg in args:
        print(f"  {each_arg}")
    print(
        f"\n  third: {third}"
        f"\n  fourth: {fourth}"
    )
    for name, arg in kwargs.items():
        print(f"  {name}: {arg}")
