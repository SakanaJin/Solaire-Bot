import inspect
from functools import wraps

class Depends:
    def __init__(self, dependency):
        self.dependency = dependency

def inject(func):
    sig = inspect.signature(func)
    new_params = [
        param for param in sig.parameters.values()
        if not isinstance(param.default, Depends)
    ]
    new_sig = sig.replace(parameters=new_params)
    @wraps(func)
    async def wrapper(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)
        cleanup = []
        cache = {}
        try:
            for name, param in sig.parameters.items():
                if name in bound.arguments:
                    continue
                default = param.default
                if isinstance(default, Depends):
                    value, finalizer = await resolve_dependency(default.dependency, bound.arguments, cache)
                    bound.arguments[name] = value
                    if finalizer:
                        cleanup.append(finalizer)
            return await func(*bound.args, **bound.kwargs)
        finally:
            for finalizer in reversed(cleanup):
                finalizer()
    wrapper.__signature__ = new_sig
    return wrapper


async def resolve_dependency(func, parent_args=None, cache=None):
    parent_args = parent_args or {}
    cache = cache or {}
    if func in cache:
        return cache[func]
    sig = inspect.signature(func)
    kwargs = {}
    cleanup = []
    for name, param in sig.parameters.items():
        if name in parent_args:
            kwargs[name] = parent_args[name]
        elif isinstance(param.default, Depends):
            value, finalizer = await resolve_dependency(param.default.dependency, parent_args, cache)
            kwargs[name] = value
            if finalizer:
                cleanup.append(finalizer)
    if inspect.iscoroutinefunction(func):
        result = await func(**kwargs)
    else:
        result = func(**kwargs)
    if inspect.isgenerator(result):
        gen = result
        value = next(gen)
        def finalizer():
            try:
                next(gen)
            except StopIteration:
                pass
        return value, finalizer
    cache[func] = (result, None)
    return result, None