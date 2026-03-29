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
        try:
            for name, param in sig.parameters.items():
                if name in bound.arguments:
                    continue
                default = param.default
                if isinstance(default, Depends):
                    dep_func = default.dependency
                    value, finalizer = await resolve_dependency(dep_func)
                    bound.arguments[name] = value
                    if finalizer:
                        cleanup.append(finalizer)
            return await func(*bound.args, **bound.kwargs)
        finally:
            for finalizer in reversed(cleanup):
                finalizer()
    wrapper.__signature__ = new_sig
    return wrapper

async def resolve_dependency(func):
    if inspect.iscoroutinefunction(func):
        result = await func()
        return result, None
    result = func()
    if inspect.isgenerator(result):
        gen = result
        value = next(gen)
        def finalizer():
            try:
                next(gen)
            except StopIteration:
                pass
        return value, finalizer
    return result, None