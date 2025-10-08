from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from pymongo import MongoClient

# Replace with your actual API token from BotFather
API_TOKEN = '7704955106:AAFEJKG0O2sONGaR6ZQNnRSwZ79sYqOriIc'

# MongoDB configuration – replace with your own MongoDB URI if needed
MONGO_URI = "mongodb+srv://herukosupplier_db_user:ZwLZCi4O46uic1Wv@cluster0.k0d7xeb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # or your MongoDB connection string
client = MongoClient(MONGO_URI)
db = client["xAkairoo"]
filters_collection = db["filters"]
users_collection = db["users"]

# Set your owner Telegram ID (only the owner can use certain commands)
OWNER_ID = 8156708830  # Replace with your actual Telegram user ID

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Add user to database if not already present
    user = update.effective_user
    users_collection.update_one(
        {"user_id": user.id},
        {"$setOnInsert": {"user_id": user.id}},
        upsert=True
    )
    
    image_url = "https://files.catbox.moe/j7u2pk.jpg"  # Replace with your image URL
    # Use the requested link scheme for the user mention:
    mention = f'<a href="tg://openmessage?user_id={user.id}">{user.full_name}</a>'
    caption = (
        f"<b>𝖧ello {mention}, 𝖭𝗂𝖼𝖾 𝗍𝗈 𝗆𝖾𝖾𝗍 𝗒𝗈𝗎 💌</b>\n"
        "<b>I ᴀᴍ ᴀ ᴄᴜsᴛᴏᴍ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴛᴇᴀᴍ ...𝗢ʀ𝐛ɪɴᴇx𝗫 𝐍ᴇᴛᴡᴏʀᴋ</b>\n\n"
        '<b>❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ  :- <a href="https://t.me/xAkairo">𝘼𝙠𝙖𝙞𝙧𝙤</a></b>'
    )
    
    # Inline buttons arranged in three rows:
    buttons = [
        [InlineKeyboardButton("➕ 𝑳𝒆𝒕𝒔 𝑹𝒐𝒍𝒍 𝑩𝒂𝒃𝒚 ➕", url="http://t.me/GFilterBotRobot?startgroup=botstart")],
        [
            InlineKeyboardButton("❖ 𝑺𝒖𝒑𝒑𝒐𝒓𝒕 𝑪𝒉𝒂𝒕 ❖", url="https://t.me/Thronex_Chats"),
            InlineKeyboardButton("❖ 𝑺𝒖𝒑𝒑𝒐𝒓𝒕 𝑪𝒉𝒂𝒏𝒏𝒆𝒍 ❖", url="https://t.me/ThronexCodex")
        ],
        [InlineKeyboardButton("𝑶𝒘𝒏𝒆𝒓 🌐", url="https://t.me/xAkairo")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_photo(
        photo=image_url,
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def set_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Expecting format: /setfilter Keyword - Title - Link
    args = update.message.text.split(" ", 1)
    if len(args) < 2:
        await update.message.reply_text("Usage: /setfilter Keyword - Title - Link")
        return

    try:
        # Split based on " - " exactly into 3 parts: Keyword, Title, and Link
        keyword, text, link = [part.strip() for part in args[1].split(" - ", 2)]
    except ValueError:
        await update.message.reply_text("Incorrect format. Please use: /setfilter Keyword - Title - Link")
        return

    keyword_lower = keyword.lower()
    filters_collection.update_one(
        {"keyword": keyword_lower},
        {"$set": {"text": text, "link": link}},
        upsert=True
    )
    await update.message.reply_text(f"Filter set for keyword '{keyword_lower}'.")


async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /removefilter <keyword>")
        return

    keyword = " ".join(context.args).strip().lower()
    result = filters_collection.delete_one({"keyword": keyword})
    if result.deleted_count:
        await update.message.reply_text(f"Filter removed for keyword '{keyword}'.")
    else:
        await update.message.reply_text("This filter does not exist.")


async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    filters_cursor = filters_collection.find()
    filters_list = [f"{doc['keyword']}: {doc['text']}" for doc in filters_cursor]
    if filters_list:
        await update.message.reply_text("Current filters:\n" + "\n".join(filters_list))
    else:
        await update.message.reply_text("No filters have been set.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    user_count = users_collection.count_documents({})
    await update.message.reply_text(f"Total users: {user_count}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Only owner can use this command.
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Ensure the broadcast command is used as a reply.
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to the message you want to broadcast.")
        return

    from_chat_id = update.message.reply_to_message.chat_id
    message_id = update.message.reply_to_message.message_id

    users = list(users_collection.find())
    success = 0
    failure = 0

    for user in users:
        try:
            await context.bot.forward_message(
                chat_id=user["user_id"],
                from_chat_id=from_chat_id,
                message_id=message_id
            )
            success += 1
        except Exception as e:
            logger.error(f"Failed to forward message to {user['user_id']}: {e}")
            failure += 1

    await update.message.reply_text(
        f"Broadcast complete.\nSuccess: {success}\nFailure: {failure}"
    )

async def reply_to_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()
    # Load all filters from MongoDB and check if any keyword exists in the message.
    for filter_doc in filters_collection.find():
        if filter_doc["keyword"] in message_text:
            # Hyperlink the text using HTML formatting
            reply_text = f'<b><a href="{filter_doc["link"]}">{filter_doc["text"]}</a></b>'
            button = InlineKeyboardButton("🝰 𝗪𝗮𝘁𝗰𝗵 𝗡𝗼𝘄 🝰", url=filter_doc["link"])
            reply_markup = InlineKeyboardMarkup([[button]])
            await update.message.reply_text(
                reply_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            break  # Only respond to the first matching keyword


def main():
    application = Application.builder().token(API_TOKEN).build()

    # Commands available to everyone
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("listfilters", list_filters))
    
    # Owner-only commands
    application.add_handler(CommandHandler("setfilter", set_filter))
    application.add_handler(CommandHandler("removefilter", remove_filter))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Respond to any text messages that are not commands.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keyword))

    application.run_polling()


if __name__ == "__main__":
    main()
