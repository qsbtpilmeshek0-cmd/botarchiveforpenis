# I LOVE DESH BEARCH

import os
import io
import uuid
import dropbox
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from aiogram.filters import Command
from dotenv import load_dotenv
import logging

load_dotenv()

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
ARCHIVE_FOLDER = "/passports"
SECRET_CODE = "Q_FBR_PASSPORTS/DATA.GB$04743"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация Dropbox
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Проверка существования папки
try:
    dbx.files_get_metadata(ARCHIVE_FOLDER)
    logger.info(f"Папка {ARCHIVE_FOLDER} уже существует ✅")
except dropbox.exceptions.ApiError:
    dbx.files_create_folder_v2(ARCHIVE_FOLDER)
    logger.info(f"Создана папка {ARCHIVE_FOLDER} ✅")


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    file_bytes = await bot.download_file(file_info.file_path)
    
    # Генерация уникального имени файла
    ext = ".jpg"
    filename = f"{message.from_user.id}_{uuid.uuid4().hex}{ext}"
    dropbox_path = f"{ARCHIVE_FOLDER}/{filename}"
    
    try:
        dbx.files_upload(file_bytes.read(), dropbox_path)
        await message.reply("✅ Фото успешно заархивировано!")
    except Exception as e:
        logger.error(f"Ошибка при загрузке фото: {e}")
        await message.reply("❌ Ошибка при архивации фото.")


@dp.message(F.text)
async def handle_text(message: types.Message):
    text = message.text.strip()
    
    if text == SECRET_CODE:
        # Выдаём все файлы из архива
        try:
            files = dbx.files_list_folder(ARCHIVE_FOLDER).entries
            if not files:
                await message.reply("Архив пуст.")
                return
            
            for f in files:
                if isinstance(f, dropbox.files.FileMetadata):
                    metadata, res = dbx.files_download(f.path_lower)
                    await message.reply_document(FSInputFile(io.BytesIO(res.content), filename=f.name))
        except Exception as e:
            logger.error(f"Ошибка при выдаче архива: {e}")
            await message.reply("❌ Ошибка доступа к архиву.")
    else:
        await message.reply("Неверный код или команда.")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply("Привет! Пришли фото в формате JPG/PNG для архивации.\n"
                        "Для получения архива используйте секретный код.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
    
