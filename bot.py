import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# Load environment variables
API_TOKEN = os.getenv("API_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["acx_bot"]
filters_collection = db["filters"]
users_collection = db["users"]

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_collection.update_one(
        {"user_id": user.id},
        {"$setOnInsert": {"user_id": user.id}},
        upsert=True
    )

    image_url = "https://files.catbox.moe/dc8yr1.jpg"
    mention = f'<a href="tg://openmessage?user_id={user.id}">{user.first_name}</a>'
    caption = (
        f"Hi {mention}, nice to meet you 🙌\n"
        "I am a Global Filter Bot. I can help you manage global filters across all groups.\n"
        'By <a href="https://t.me/ORBINEXX_NETWORK">ORBINEXX Network</a>'
    )

    buttons = [
        [InlineKeyboardButton("Let's Roll Baby", url="http://t.me/GFilterBotRobot?startgroup=botstart")],
        [
            InlineKeyboardButton("Support Chat", url="https://t.me/ORBINEXX_SOCIETY"),
            InlineKeyboardButton("Support Channel", url="https://t.me/ORBINEXX_NETWORK")
        ],
        [InlineKeyboardButton("Owner", url="https://t.me/NOONEISMINEE")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_photo(
        photo=image_url,
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


# Set filter command
async def set_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    args = update.message.text.split(" ", 1)
    if len(args) < 2:
        await update.message.reply_text("Usage: /setfilter Keyword - Title - Link")
        return

    try:
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


# Remove filter command
async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


# List filters command
async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters_cursor = filters_collection.find()
    filters_list = [f"{doc['keyword']}: {doc['text']}" for doc in filters_cursor]
    if filters_list:
        await update.message.reply_text("Current filters:\n" + "\n".join(filters_list))
    else:
        await update.message.reply_text("No filters have been set.")


# Stats command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    user_count = users_collection.count_documents({})
    await update.message.reply_text(f"Total users: {user_count}")


# Broadcast command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to the message you want to broadcast.")
        return

    message = update.message.reply_to_message
    users = list(users_collection.find())
    success, failure = 0, 0

    for user in users:
        try:
            await message.copy(chat_id=user["user_id"])
            success += 1
        except Exception as e:
            logger.error(f"Failed to send message to {user['user_id']}: {e}")
            failure += 1

    await update.message.reply_text(
        f"Broadcast complete.\nSuccess: {success}\nFailure: {failure}"
    )


# Reply to keywords
async def reply_to_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.lower()
    for filter_doc in filters_collection.find():
        if filter_doc["keyword"] in message_text:
            reply_text = f'<a href="{filter_doc["link"]}">{filter_doc["text"]}</a>'
            button = InlineKeyboardButton(
                "🔰 WATCH & DOWNLOAD NOW 🔰",
                url=filter_doc["link"]
            )
            reply_markup = InlineKeyboardMarkup([[button]])
            await update.message.reply_text(
                reply_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            break


def main():
    # Application builder use karo with connection pooling
    application = Application.builder().token(API_TOKEN).pool_timeout(30).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("listfilters", list_filters))
    application.add_handler(CommandHandler("setfilter", set_filter))
    application.add_handler(CommandHandler("removefilter", remove_filter))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keyword))

    # Error handler add karo
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)

    # Run the bot
    logger.info("Bot starting...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
