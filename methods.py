from functools import partial
import typing as t

class MethodError(Exception):
    pass

functype = t.Callable[..., str]

methods: dict[str, functype] = {}

def _method_adder(name: str, func: functype):
    methods[name] = func
    return func

def add_to_methods(arg: functype | str):
    if isinstance(arg, str):
        return partial(_method_adder, arg)
    
    else:
        _method_adder(arg.__name__, arg)
        return arg

@add_to_methods
def ls():
    return ", ".join(methods)