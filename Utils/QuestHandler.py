quest_handlers = {}

def register_quest(qtype):
    def decorator(func):
        quest_handlers[qtype] = func
        return func
    return decorator