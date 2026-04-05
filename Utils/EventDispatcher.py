event_handlers = {}

def register_event(name):
    def decorator(func):
        event_handlers[name] = func
        return func
    return decorator

async def dispatch_event(name: str, **kwargs):
    handler = event_handlers.get(name)
    if not handler:
        raise ValueError(f"{name} does not have an event handler")
    await handler(**kwargs)