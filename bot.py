# I LOVE DESH BEARCH

import os
import uuid
import dropbox
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
SECRET_CODE = "Q_FBR_PASSPORTS/DATA.GB$04743"
PASS_FOLDER = "/RPGPassportBot"

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Проверяем существование папки в Dropbox
try:
    dbx.files_get_metadata(PASS_FOLDER)
except dropbox.exceptions.ApiError:
    dbx.files_create_folder_v2(PASS_FOLDER)

# Команда /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer("Отправьте фото своего паспорта. Он будет заархивирован")

# Обработка фото
@dp.message(types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    file_id = str(uuid.uuid4())  # уникальное имя
    file_info = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    filename = f"{file_id}.jpg"
    path = f"{PASS_FOLDER}/{filename}"

    try:
        dbx.files_upload(file_bytes.read(), path)
        await message.answer(f"Паспорт успешно заархивирован под именем")
    except Exception as e:
        await message.answer(f"Ошибка при архивации: {e}")

# Команда показать архив по секретному коду
@dp.message()
async def handle_secret_code(message: types.Message):
    if message.text == SECRET_CODE:
        try:
            res = dbx.files_list_folder(PASS_FOLDER)
            if not res.entries:
                await message.answer("Архив пустой.")
                return

            for entry in res.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    metadata, file_content = dbx.files_download(entry.path_lower)
                    await message.answer_document(file_content.content, filename=entry.name)
        except Exception as e:
            await message.answer(f"Ошибка при выдаче архива: {e}")

# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
    
