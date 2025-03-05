from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext
import asyncio
import logging
//
TOKEN = "8052336413:AAFaMV7Uw0g007KQhLJuEXr_fT8Oer3PcFg"
SOURCE_GROUP = -1002392685644
TARGET_GROUPS = [-1002462989094, -1002416697334, -1002391114315]

bot = ApplicationBuilder().token(TOKEN).build()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def forward_post(update: Update, context: CallbackContext):
    """ xabarlarni xona2, xona3 va xona4 ga jo'natish """
    if update.message and update.message.chat_id == SOURCE_GROUP:
        media_group_id = update.message.media_group_id

        if media_group_id:
            if media_group_id not in context.bot_data:
                context.bot_data[media_group_id] = {"messages": [], "task": None}

            context.bot_data[media_group_id]["messages"].append(update.message)

            if context.bot_data[media_group_id]["task"]:
                context.bot_data[media_group_id]["task"].cancel()

            context.bot_data[media_group_id]["task"] = asyncio.create_task(send_media(update, context, media_group_id))

        else:
            for group in TARGET_GROUPS:
                await send_with_retry(update.message.copy(chat_id=group))

async def send_media(update: Update, context: CallbackContext, media_group_id: str):
    """ Barcha media fayllarni to'plab, birga jo'natish """
    await asyncio.sleep(5)

    if media_group_id in context.bot_data:
        media_list = []
        messages = sorted(context.bot_data[media_group_id]["messages"], key=lambda m: m.message_id)

        for msg in messages:
            if msg.photo:
                media_list.append(InputMediaPhoto(msg.photo[-1].file_id, caption=msg.caption if msg.caption else ""))
            elif msg.video:
                media_list.append(InputMediaVideo(msg.video.file_id, caption=msg.caption if msg.caption else ""))

        for group in TARGET_GROUPS:
            await send_with_retry(context.bot.send_media_group(chat_id=group, media=media_list))

        del context.bot_data[media_group_id]

async def send_with_retry(send_func, retries=3, delay=5):
    """ Xatolik yuz bersa, so‘rovni qayta yuborish """
    for attempt in range(retries):
        try:
            await send_func
            return
        except Exception as e:
            logger.error(f"Xatolik ({attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error("Xabar yuborilmadi!")

bot.add_handler(MessageHandler(filters.ALL, forward_post))

bot.run_polling()
