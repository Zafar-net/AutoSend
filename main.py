from telegram import Bot, Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext

TOKEN = "8052336413:AAFaMV7Uw0g007KQhLJuEXr_fT8Oer3PcFg"
DEST_GROUP = [-1002462989094, -1002416697334, -1002391114315]
MAIN_GROUP = -1002392685644

bot = Bot(token=TOKEN)

async def forward_messages(update: Update, context: CallbackContext):
    if update.message and update.message.chat_id == MAIN_GROUP:
        if update.message.media_group_id:
            media_messages = context.bot_data.get(update.message.media_group_id, [])
            media_messages.append(update.message)
            context.bot_data[update.message.media_group_id] = media_messages

            if len(media_messages) == 1:
                return

            media_list = []
            for msg in media_messages:
                if msg.photo:
                    media_list.append(
                        InputMediaPhoto(msg.photo[-1].file_id, caption=msg.caption if msg.caption else ""))
                elif msg.video:
                    media_list.append(InputMediaVideo(msg.video.file_id, caption=msg.caption if msg.caption else ""))

            for group in DEST_GROUP:
                await context.bot.send_media_group(
                    chat_id=group,
                    media=media_list
                )
        else:
            for group in DEST_GROUP:
                await context.bot.copy_message(
                    chat_id=group,
                    from_chat_id=MAIN_GROUP,
                    message_id=update.message.message_id
                )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, forward_messages))

app.run_polling()
