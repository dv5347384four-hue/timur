import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- КОНФИГУРАЦИЯ ---
# Вставьте свой токен сюда (в кавычках)
API_TOKEN = "8501713967:AAFH3WqvDZN_xWL6EKVXiAhjQNdy9nZHpeE"

# Вставьте свой ID цифрами (без кавычек)
ADMIN_ID = 5085599029

# --- НАСТРОЙКА ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- МАШИНА СОСТОЯНИЙ (FSM) ---
# Нам нужно состояние, чтобы понимать, когда пользователь пишет сообщение
class ContactForm(StatesGroup):
    waiting_for_message = State()

# --- ОБРАБОТЧИКИ (HANDLERS) ---

# 1. Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Я бот-помощник.\n\n"
        "Если вы хотите связаться с владельцем, просто напишите ваше сообщение "
        "или опишите суть предложения прямо здесь. Я передам!"
    )
    # Переводим пользователя в режим ожидания сообщения
    await state.set_state(ContactForm.waiting_for_message)

# 2. Получение сообщения от пользователя
@dp.message(ContactForm.waiting_for_message)
async def process_message(message: types.Message, state: FSMContext):
    # Данные о пользователе
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text

    # Формируем ссылку на пользователя (чтобы вы могли нажать и написать ему)
    # Если есть юзернейм - ссылка на него, если нет - ссылка через ID
    user_link = f"tg://user?id={user_id}"
    
    # Текст для админа
    admin_text = (
        f"🔔 **Новая заявка!**\n\n"
        f"👤 **От:** {user_name}\n"
        f"🆔 **ID:** `{user_id}`\n"
        f"📧 **Username:** @{username if username else 'Нет'}\n\n"
        f"📝 **Сообщение:**\n{text}"
    )

    # Кнопка для быстрого ответа
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить в ЛС", url=user_link)]
    ])

    # Отправляем сообщение ВАМ (Админу)
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=keyboard, parse_mode="Markdown")
        # Ответ пользователю
        await message.answer("✅ Ваше сообщение отправлено! Скоро вам ответят.")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при отправке. Попробуйте позже.")
        logging.error(f"Ошибка отправки админу: {e}")

    # Сбрасываем состояние, чтобы пользователь мог написать снова через /start или просто новым сообщением
    await state.clear()

# Если пользователь пишет без команды /start, тоже считаем это заявкой
@dp.message()
async def any_message(message: types.Message, state: FSMContext):
    # Перенаправляем логику в ту же функцию
    await process_message(message, state)

# --- ЗАПУСК ---
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
