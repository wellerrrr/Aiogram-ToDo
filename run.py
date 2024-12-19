import asyncio
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import TOKEN, DATABASE_URL
from database.models import Base
from handlers import start_handler, add_task_callback, process_add_task, AddTask, list_tasks_handler, update_task_handler, delete_task_handler, delete_completed_tasks_handler, list_tasks_from_keyboard, list_tasks_callback, add_task_from_keyboard

logging.basicConfig(level=logging.INFO)

async def init_db():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return async_session

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    session_maker = await init_db()

    dp.message.register(start_handler, CommandStart())
    dp.callback_query.register(add_task_callback, F.data == "add_task")
    dp.message.register(process_add_task, AddTask.waiting_for_task)
    dp.message.register(list_tasks_from_keyboard, F.text == "Список задач")
    dp.callback_query.register(update_task_handler, F.data.startswith("task_"))
    dp.message.register(delete_task_handler, Command("delete"))
    dp.callback_query.register(delete_completed_tasks_handler, F.data == "delete_completed")
    dp.callback_query.register(list_tasks_callback, F.data == "list_tasks")
    dp.message.register(add_task_from_keyboard, F.text == "Добавить задачу")

    async def on_startup():
        bot_data = await bot.get_me()
        print(f"Бот @{bot_data.username} успешно запущен!")

    dp.startup.register(on_startup)

    async def db_session_middleware(handler, event, data):
        async with session_maker() as session:
            if isinstance(event, types.Message):
                 data['session'] = session
                 data['bot'] = bot
            if isinstance(event, types.CallbackQuery):
                 data['session'] = session
                 data["message"] = event.message
            return await handler(event, data)

    dp.message.middleware(db_session_middleware)
    dp.callback_query.middleware(db_session_middleware)
    
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")