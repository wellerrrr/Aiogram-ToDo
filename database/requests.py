from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from database.models import Task


async def add_task_db(session: AsyncSession, user_id: int, task: str):
    new_task = Task(user_id=user_id, task=task)
    session.add(new_task)
    await session.commit()


async def get_tasks_db(session: AsyncSession, user_id: int) -> List[Task]:
    query = select(Task).where(Task.user_id == user_id)
    result = await session.execute(query)
    tasks = result.scalars().all()
    return list(tasks)


async def update_task_db(session: AsyncSession, task_id: int):
    query = update(Task).where(Task.id == task_id).values(completed=True)
    await session.execute(query)
    await session.commit()


async def delete_task_db(session: AsyncSession, task_id: int):
    query = delete(Task).where(Task.id == task_id)
    await session.execute(query)
    await session.commit()