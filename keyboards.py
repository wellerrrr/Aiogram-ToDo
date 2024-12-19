from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton


def get_start_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Добавить задачу")],
        [KeyboardButton(text="Список задач")],
    ], resize_keyboard=True)
    return keyboard

def get_start_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить задачу", callback_data="add_task")
    builder.button(text="Список задач", callback_data="list_tasks")
    builder.adjust(1)
    return builder.as_markup()

def get_tasks_inline_keyboard(tasks):
    builder = InlineKeyboardBuilder()
    for task in tasks:
        status_symbol = "✅" if task.completed else "◻️"
        builder.button(text=f"{status_symbol} {task.task}", callback_data=f"task_{task.id}")
    builder.button(text="Удалить выполненные", callback_data="delete_completed")
    builder.adjust(1)
    return builder.as_markup()


def get_add_task_keyboard():
      keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Список задач"), KeyboardButton(text="Добавить задачу")]
    ], resize_keyboard=True)
      return keyboard