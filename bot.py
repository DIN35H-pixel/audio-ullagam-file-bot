import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import create_deep_linked_url


BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
FORCE_CHANNEL = os.environ["FORCE_CHANNEL"]
STORAGE_CHANNEL_ID = int(os.environ["STORAGE_CHANNEL_ID"])
RENDER_URL = os.environ["RENDER_URL"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]


async def is_subscribed(bot, user_id):

    try:
        member = await bot.get_chat_member(
            chat_id=FORCE_CHANNEL,
            user_id=user_id
        )

        if member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ]:
            return True

        if (
            member.status == ChatMemberStatus.RESTRICTED
            and member.is_member
        ):
            return True

        return False

    except Exception:
        return False


async def send_force_subscribe(update, context, payload=None):

    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Join Audio Ullagam",
                url=f"https://t.me/{FORCE_CHANNEL.lstrip('@')}"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Joined - Check Again",
                callback_data=f"check:{payload or 'none'}"
            )
        ]
    ]

    text = (
        "🎧 <b>Audio Ullagam</b>\n\n"
        "இந்த Bot-ஐ பயன்படுத்துவதற்கு முன் "
        "எங்கள் Telegram Channel-ஐ Join செய்யுங்கள்.\n\n"
        "📖 Tamil Audio Stories\n"
        "⚔️ Fantasy • Warrior • Adventure\n"
        "🔥 New Episodes தொடர்ந்து!\n\n"
        "👇 முதலில் Channel-ஐ Join செய்து "
        "<b>Joined - Check Again</b> அழுத்துங்கள்."
    )

    markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=markup
        )
    else:
        await update.message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=markup
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    payload = None

    if context.args:
        payload = context.args[0]

    subscribed = await is_subscribed(
        context.bot,
        update.effective_user.id
    )

    if not subscribed:

        await send_force_subscribe(
            update,
            context,
            payload
        )

        return

    if payload and payload.startswith("file_"):

        try:

            message_id = int(
                payload.replace("file_", "")
            )

            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=STORAGE_CHANNEL_ID,
                message_id=message_id,
                protect_content=True
            )

        except Exception:

            await update.message.reply_text(
                "❌ இந்த Audio தற்போது கிடைக்கவில்லை."
            )

        return

    await update.message.reply_text(
        "🎧 <b>வணக்கம்!</b>\n\n"
        "Audio Ullagam File Bot-க்கு வரவேற்கிறோம்! ❤️\n\n"
        "📖 தமிழ் Audio Stories\n"
        "⚔️ Fantasy • Warrior • Adventure\n"
        "🎙️ புதிய Episodes தொடர்ந்து!\n\n"
        "கதையின் Audio Link-ஐ open செய்து "
        "இங்கே கேளுங்கள்.",
        parse_mode="HTML"
    )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    payload = query.data.replace("check:", "")

    subscribed = await is_subscribed(
        context.bot,
        query.from_user.id
    )

    if not subscribed:

        await query.message.reply_text(
            "❌ இன்னும் Channel Join செய்யவில்லை.\n\n"
            "முதலில் Audio Ullagam Channel-ஐ Join செய்யுங்கள்."
        )

        return

    if payload.startswith("file_"):

        try:

            message_id = int(
                payload.replace("file_", "")
            )

            await context.bot.copy_message(
                chat_id=query.from_user.id,
                from_chat_id=STORAGE_CHANNEL_ID,
                message_id=message_id,
                protect_content=True
            )

        except Exception:

            await query.message.reply_text(
                "❌ Audio கிடைக்கவில்லை."
            )

    else:

        await query.message.reply_text(
            "✅ நீங்கள் Channel-ஐ Join செய்துவிட்டீர்கள்!"
        )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"🆔 Your Telegram ID:\n\n"
        f"<code>{update.effective_user.id}</code>",
        parse_mode="HTML"
    )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ இந்த command Admin-க்கு மட்டும்."
        )

        return

    message = update.effective_message

    try:

        copied = await context.bot.copy_message(
            chat_id=STORAGE_CHANNEL_ID,
            from_chat_id=update.effective_chat.id,
            message_id=message.message_id
        )

        bot_info = await context.bot.get_me()

        link = create_deep_linked_url(
            bot_info.username,
            f"file_{copied.message_id}"
        )

        await update.message.reply_text(
            "✅ <b>Audio Added Successfully!</b>\n\n"
            f"🔗 <b>Share Link:</b>\n{link}",
            parse_mode="HTML"
        )

    except Exception:

        await update.message.reply_text(
            "❌ File save செய்ய முடியவில்லை."
        )


def main():

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("myid", myid)
    )

    application.add_handler(
        CallbackQueryHandler(
            check_join,
            pattern="^check:"
        )
    )

    application.add_handler(
        MessageHandler(
            filters.AUDIO | filters.Document.ALL,
            receive_file
        )
    )

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        url_path=WEBHOOK_SECRET,
        webhook_url=f"{RENDER_URL}/{WEBHOOK_SECRET}",
        secret_token=WEBHOOK_SECRET
    )


if __name__ == "__main__":
    main()
