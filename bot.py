# I LOVE DESH BEARCHHHHH

import os
import logging
import io
import dropbox
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Text
from aiogram.types import FSInputFile
from datetime import datetime

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
TOKEN = os.environ.get("BOT_TOKEN")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
SECRET_CODE = "Q_FBR_PASSPORTS/DATA.GB$04743"  # Секретный код для выдачи всех фото
PASS_FOLDER = "/passports/"

# Инициализация бота и Dropbox
bot = Bot(token=TOKEN)
dp = Dispatcher()

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Проверка существования папки в Dropbox, создаём если нет
try:
    dbx.files_get_metadata(PASS_FOLDER)
    logger.info(f"Папка {PASS_FOLDER} уже существует ✅")
except dropbox.exceptions.ApiError:
    dbx.files_create_folder_v2(PASS_FOLDER)
    logger.info(f"Папка {PASS_FOLDER} создана ✅")

# Обработка фото
@dp.message(F.content_type.in_({"photo"}))
async def handle_photo(message: types.Message):
    photo = message.photo[-1]  # Берём фото с максимальным разрешением
    file_info = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    ext = ".jpg"  # Telegram всегда присылает в формате jpg
    filename = f"{message.from_user.id}_{timestamp}{ext}"
    dropbox_path = PASS_FOLDER + filename

    try:
        dbx.files_upload(file_bytes.read(), dropbox_path)
        await message.answer("Фото успешно архивировано ✅")
        logger.info(f"Фото пользователя {message.from_user.id} сохранено как {filename}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении фото: {e}")
        await message.answer("Ошибка при архивировании. Обратитесь к администратору.")

# Обработка текста
@dp.message(F.content_type.in_({"text"}))
async def handle_text(message: types.Message):
    text = message.text.strip()

    if text == SECRET_CODE:
        # Получаем все файлы из папки
        try:
            res = dbx.files_list_folder(PASS_FOLDER)
            if not res.entries:
                await message.answer("Архив пустой.")
                return

            # Отправляем файлы по одному
            for entry in res.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    metadata, f = dbx.files_download(entry.path_lower)
                    file_bytes = io.BytesIO(f.content)
                    file_bytes.name = entry.name
                    await message.answer_document(FSInputFile(file_bytes))
            logger.info(f"Все файлы отправлены пользователю {message.from_user.id}")
        except Exception as e:
            logger.error(f"Ошибка при выдаче архива: {e}")
            await message.answer("Ошибка при выдаче архива. Обратитесь к администратору.")
    else:
        await message.answer("Неверный код или команда.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
    
    
