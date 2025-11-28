# I LOVE DESH BEARCHHHHH
import os
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
import dropbox

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные среды
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")

if not BOT_TOKEN or not DROPBOX_TOKEN:
    raise ValueError("❌ BOT_TOKEN или DROPBOX_TOKEN отсутствуют в переменных окружения!")

# Инициализация
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Папка архива
ARCHIVE_FOLDER = "/PASSPORTS_ARCHIVE"


# --- Проверяем и создаём папку в Dropbox ---
def ensure_dropbox_folder():
    try:
        dbx.files_get_metadata(ARCHIVE_FOLDER)
        logger.info("Папка уже существует.")
    except dropbox.exceptions.ApiError:
        logger.info("Папка отсутствует — создаю.")
        dbx.files_create_folder_v2(ARCHIVE_FOLDER)


ensure_dropbox_folder()


# --- Команда /start ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Я архиватор фотографий.\n"
        "Отправь мне фото — и я сохраню его в Dropbox.\n"
        "Команда для выдачи сохранённых фото: /get"
    )


# --- Сохранение фото ---
@dp.message(F.photo)
async def save_photo(message: types.Message):
    try:
        # Получаем файл
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)

        # Уникальное имя
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_name = f"{message.from_user.id}_{timestamp}.jpg"

        dropbox_path = f"{ARCHIVE_FOLDER}/{unique_name}"

        # Загружаем
        dbx.files_upload(file_bytes.read(), dropbox_path, mute=True)

        await message.answer("📁 Фото успешно архивировано!")
    except Exception as e:
        logger.error(f"Ошибка архивации: {e}")
        await message.answer("❌ Ошибка при сохранении фотографии.")


# --- Выдача архивированных фото ---
@dp.message(Command("get"))
async def get_archived(message: types.Message):
    try:
        # Получаем список файлов
        files = dbx.files_list_folder(ARCHIVE_FOLDER).entries

        if not files:
            return await message.answer("📂 Архив пуст.")

        # Фильтруем только файлы конкретного пользователя
        user_files = [f for f in files if f.name.startswith(str(message.from_user.id))]

        if not user_files:
            return await message.answer("🤷 У вас нет сохранённых фото.")

        # Отправляем файлы пользователю
        for f in user_files:
            metadata, res = dbx.files_download(f"{ARCHIVE_FOLDER}/{f.name}")
            await message.answer_document(types.BufferedInputFile(
                res.content,
                filename=f.name
            ))

    except Exception as e:
        logger.error(f"Ошибка выдачи архива: {e}")
        await message.answer("❌ Ошибка при выдаче архива.")


# --- Запуск ---
if __name__ == "__main__":
    logger.info("Бот запущен...")
    dp.run_polling(bot)
    
