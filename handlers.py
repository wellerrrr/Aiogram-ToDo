from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.requests import add_task_db, get_tasks_db, update_task_db, delete_task_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Task
from keyboards import get_start_keyboard, get_start_inline_keyboard, get_tasks_inline_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot

class AddTask(StatesGroup):
    waiting_for_task = State()


async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = get_start_keyboard()
    inline_keyboard = get_start_inline_keyboard()
    await message.answer(
        "Привет! Я твой туду-бот. Выбери действие:",
        reply_markup=inline_keyboard
    )
    await message.answer("Используй кнопки для взаимодействия", reply_markup=keyboard)


async def add_task_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши задачу, которую хочешь добавить")
    await state.set_state(AddTask.waiting_for_task)
    await callback.answer()

async def list_tasks_callback(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    builder, text = await list_tasks_handler(callback.message, session, callback.from_user.id)
    if isinstance(builder, InlineKeyboardBuilder):
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    else:
        await callback.message.answer(text=text, reply_markup=builder)

async def process_add_task(message: types.Message, state: FSMContext, session: AsyncSession):
    task_text = message.text
    if task_text == "Список задач":
        await message.answer("Введите текст задачи")
        return
    if task_text == "Добавить задачу" and await state.get_state() == AddTask.waiting_for_task:
        await message.answer("Введите текст задачи")
        return
    user_id = message.from_user.id
    await add_task_db(session, user_id, task_text)
    keyboard = get_start_keyboard()
    await message.answer("Задача добавлена!", reply_markup=keyboard)
    await state.clear()
async def add_task_from_keyboard(message: types.Message, state: FSMContext, bot: Bot):
    await bot.send_message(message.from_user.id, "Напиши задачу, которую хочешь добавить", reply_markup=get_start_keyboard())
    await state.set_state(AddTask.waiting_for_task)
    
async def list_tasks_handler(message: types.Message, session: AsyncSession, user_id: int):
    tasks = await get_tasks_db(session, user_id)

    if not tasks:
        builder = InlineKeyboardBuilder()
        builder.button(text="Добавить задачу", callback_data="add_task")
        return builder.as_markup(), "У вас пока нет задач."
    
    
    keyboard = get_tasks_inline_keyboard(tasks)
    return keyboard, "Ваши задачи:"


async def update_task_handler(callback: types.CallbackQuery, session: AsyncSession):
    task_id = int(callback.data.split("_")[1])
    await update_task_db(session, task_id)
    await callback.answer("Задача выполнена!")
    builder, text = await list_tasks_handler(callback.message, session, callback.from_user.id)
    if isinstance(builder, InlineKeyboardBuilder):
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text(text=text, reply_markup=builder)


async def delete_task_handler(message: types.Message, session: AsyncSession):
    try:
        task_id = int(message.text.split(" ")[1])
    except IndexError:
        await message.answer(
            "Пожалуйста, укажите ID задачи, которую хотите удалить, после команды /delete. Пример /delete 1"
        )
        return
    except ValueError:
        await message.answer("Пожалуйста, введите правильный ID задачи (число)")
        return
    await delete_task_db(session, task_id)
    await message.answer(f"Задача с ID {task_id} удалена.")

async def delete_completed_tasks_handler(callback: types.CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    query = select(Task).where(Task.user_id == user_id, Task.completed == True)
    result = await session.execute(query)
    completed_tasks = result.scalars().all()
    for task in completed_tasks:
        await delete_task_db(session, task.id)
    await callback.answer("Выполненные задачи удалены")
    builder, text = await list_tasks_handler(callback.message, session, user_id)
    if isinstance(builder, InlineKeyboardBuilder):
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text(text=text, reply_markup=builder)

async def list_tasks_from_keyboard(message: types.Message, session: AsyncSession):
    builder, text = await list_tasks_handler(message, session, message.from_user.id)
    if isinstance(builder, InlineKeyboardBuilder):
      await message.answer(text=text, reply_markup=builder.as_markup())
    else:
      await message.answer(text=text, reply_markup=builder)