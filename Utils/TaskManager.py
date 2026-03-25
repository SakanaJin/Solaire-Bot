import asyncio
from discord.ext import tasks
from sqlalchemy import select

from database import get_db
from Entities.Tasks import Task

class TaskManagerClass:
    def __init__(self):
        self.tasks = {}

    async def syncdb(self, db):
        dbtasks = db.scalars(
            select(Task)
        ).all()
        for task in self.tasks.keys():
            dbtask = next((dbtask for dbtask in dbtasks if dbtask.name == task), None)
            if not dbtask:
                newTask = Task(
                    name=task,
                    enabled=True
                )
                db.add(newTask)
            else:
                self.tasks[task]["enabled"] = dbtask.enabled
        db.commit()
    
    def register(self, taskname: str, **kwargs):
        def decorator(func):
            loop_obj = tasks.loop(**kwargs)(func)
            ready_event = asyncio.Event()
            @loop_obj.before_loop
            async def before():
                ready_event.set()
            self.tasks[taskname] = {
                "name": taskname,
                "task": loop_obj,
                "func": func,
                "enabled": True,
                "ready": ready_event
            }
            return loop_obj
        return decorator
    
    async def wait_until_ready(self):
        await asyncio.gather(*(task["ready"].wait() for task in self.tasks.values()))
    
    def startall(self) -> None:
        for task in self.tasks.values():
            if task["enabled"]:
                task["task"].start()

    async def run(self, taskname: str)-> None:
        task = self.tasks.get(taskname)
        if not taskname:
            raise NameError(f"{taskname} not found")
        await task["func"]()

    def start(self, taskname: str):
        task = self.tasks.get(taskname)
        if not taskname:
            raise NameError(f"{taskname} not found")
        if not task["task"].is_running():
            task["task"].start()

    def stop(self, taskname: str):
        task = self.tasks.get(taskname)
        if not taskname:
            raise NameError(f"{taskname} not found")
        task["task"].stop()

    def enable(self, taskname: str):
        task = self.tasks.get(taskname)
        if not taskname:
            raise NameError(f"{taskname} not found")
        task["enabled"] = True
        with get_db() as db:
            dbtask = db.execute(
                select(Task)
                .where(Task.name == taskname)
            ).scalar_one_or_none()
            dbtask.enabled = True
            db.commit()
        self.start(taskname)

    def disable(self, taskname: str):
        task = self.tasks.get(taskname)
        if not taskname:
            raise NameError(f"{taskname} not found")
        task["enabled"] = False
        with get_db() as db:
            dbtask = db.execute(
                select(Task)
                .where(Task.name == taskname)
            ).scalar_one_or_none()
            dbtask.enabled = False
            db.commit()
        self.stop(taskname)

TaskManager = TaskManagerClass()