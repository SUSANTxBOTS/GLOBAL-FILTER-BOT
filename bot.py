from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from pymongo import MongoClient
import time
import sys

# Configuration
API_TOKEN = '7704955106:AAFEJKG0O2sONGaR6ZQNnRSwZ79sYqOriIc'
MONGO_URI = "mongodb+srv://herukosupplier_db_user:ZwLZCi4O46uic1Wv@cluster0.k0d7xeb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
OWNER_IDS = [8156708830, 7125448912, 987654321, 7968389767]
BACKUP_CHANNEL = "https://t.me/your_backup_channel"

# MongoDB with better connection settings
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000, socketTimeoutMS=5000)
    client.admin.command('ping')
    db = client["xAkairo"]
    filters_collection = db["filters"]
    users_collection = db["users"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        users_collection.update_one(
            {"user_id": user.id},
            {"$setOnInsert": {"user_id": user.id}},
            upsert=True
        )
        
        image_url = "https://files.catbox.moe/vqomxt.jpg"
        mention = f'<a href="tg://openmessage?user_id={user.id}">{user.full_name}</a>'
        caption = (
            f"<b>𝖧𝖾𝗅𝗅𝗈 {mention}, 𝖭𝗂𝖼𝖾 𝗍𝗈 𝗆𝖾𝖾𝗍 𝗒𝗈𝗎 💌</b>\n"
            "<b>𝖨 𝖺𝗆 𝖺 𝖼𝗎𝗌𝗍𝗈𝗆 𝖻𝗈𝗍 𝗆𝖺𝖽𝖾 𝖿𝗈𝗋 𝗍𝖾𝖺𝗆 ...𝖮𝗋𝖻𝗂𝗇𝖾𝗑𝖷 𝖭𝖾𝗍𝗐𝗈𝗋𝗄</b>\n"
            '<b>❖ 𝖯𝗈𝗐𝖾𝗋𝖾𝖽 𝖻𝗒  :- <a href="https://t.me/xAkairo">𝘼𝙠𝙖𝙞𝙧𝙤</a></b>'
        )
        
        buttons = [
            [InlineKeyboardButton("✙ 𝖠𝖽𝖽 𝖬𝖾 𝖨𝗇 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ✙", url="http://t.me/GFilterRobot?startgroup=botstart")],
            [
                InlineKeyboardButton("˹ 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 ˼", url="https://t.me/Thronex_Chats"),
                InlineKeyboardButton("˹ 𝖴𝗉𝖽𝖺𝗍𝖾𝗌 ˼", url="https://t.me/ThronexCodex")
            ],
            [InlineKeyboardButton("˹ 𝖮𝗐𝗇𝖾𝗋 ˼", url="https://t.me/xAkairo")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.reply_photo(
            photo=image_url,
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def set_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.effective_user.id not in OWNER_IDS:
            await update.message.reply_text("𝖸𝗈𝗎 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝗎𝗍𝗁𝗈𝗋𝗂𝗓𝖾𝖽 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.")
            return

        args = update.message.text.split(" ", 1)
        if len(args) < 2:
            await update.message.reply_text("𝖴𝗌𝖺𝗀𝖾: /setfilter 𝖪𝖾𝗒𝗐𝗈𝗋𝖽 - 𝖳𝗂𝗍𝗅𝖾 - 𝖫𝗂𝗇𝗄")
            return

        try:
            keyword, text, link = [part.strip() for part in args[1].split(" - ", 2)]
        except ValueError:
            await update.message.reply_text("𝖨𝗇𝖼𝗈𝗋𝗋𝖾𝖼𝗍 𝖿𝗈𝗋𝗆𝖺𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗎𝗌𝖾: /setfilter 𝖪𝖾𝗒𝗐𝗈𝗋𝖽 - 𝖳𝗂𝗍𝗅𝖾 - 𝖫𝗂𝗇𝗄")
            return

        keyword_lower = keyword.lower()
        filters_collection.update_one(
            {"keyword": keyword_lower},
            {"$set": {"text": text, "link": link}},
            upsert=True
        )
        await update.message.reply_text(f"𝖥𝗂𝗅𝗍𝖾𝗋 𝗌𝖾𝗍 𝖿𝗈𝗋 𝗄𝖾𝗒𝗐𝗈𝗋𝖽 '{keyword_lower}'.")
    except Exception as e:
        logger.error(f"Error in set_filter: {e}")

async def remove_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.effective_user.id not in OWNER_IDS:
            await update.message.reply_text("𝖸𝗈𝗎 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝗎𝗍𝗁𝗈𝗋𝗂𝗓𝖾𝖽 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.")
            return

        if not context.args:
            await update.message.reply_text("𝖴𝗌𝖺𝗀𝖾: /removefilter <𝗄𝖾𝗒𝗐𝗈𝗋𝖽>")
            return

        keyword = " ".join(context.args).strip().lower()
        result = filters_collection.delete_one({"keyword": keyword})
        if result.deleted_count:
            await update.message.reply_text(f"𝖥𝗂𝗅𝗍𝖾𝗋 𝗋𝖾𝗆𝗈𝗏𝖾𝖽 𝖿𝗈𝗋 𝗄𝖾𝗒𝗐𝗈𝗋𝖽 '{keyword}'.")
        else:
            await update.message.reply_text("𝖳𝗁𝗂𝗌 𝖿𝗂𝗅𝗍𝖾𝗋 𝖽𝗈𝖾𝗌 𝗇𝗈𝗍 𝖾𝗑𝗂𝗌𝗍.")
    except Exception as e:
        logger.error(f"Error in remove_filter: {e}")

async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        filters_cursor = filters_collection.find()
        filters_list = [f"𝖪𝖾𝗒𝗐𝗈𝗋𝖽: {doc['keyword']} | 𝖳𝗂𝗍𝗅𝖾: {doc['text']}" for doc in filters_cursor]
        if filters_list:
            await update.message.reply_text("𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖿𝗂𝗅𝗍𝖾𝗋𝗌:\n" + "\n".join(filters_list))
        else:
            await update.message.reply_text("𝖭𝗈 𝖿𝗂𝗅𝗍𝖾𝗋𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍.")
    except Exception as e:
        logger.error(f"Error in list_filters: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.effective_user.id not in OWNER_IDS:
            await update.message.reply_text("𝖳𝖾𝗋𝖺 𝖯𝖺𝗉𝖺 @𝗑𝖥𝗅𝖾𝗑𝗒𝗒 𝖪𝗈 𝖡𝗈𝗅 𝖠𝖽𝖽 𝖪𝖺𝗋 𝖣𝖾𝗀𝖺")
            return

        user_count = users_collection.count_documents({})
        await update.message.reply_text(f"𝖳𝗈𝗍𝖺𝗅 𝗎𝗌𝖾𝗋𝗌: {user_count}")
    except Exception as e:
        logger.error(f"Error in stats: {e}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.effective_user.id not in OWNER_IDS:
            await update.message.reply_text("𝖳𝖾𝗋𝖺 𝖯𝖺𝗉𝖺 @𝗑𝖥𝗅𝖾𝗑𝗒𝗒 𝖪𝗈 𝖡𝗈𝗅 𝖠𝖽𝖽 𝖪𝖺𝗋 𝖣𝖾𝗀𝖺")
            return

        if not update.message.reply_to_message:
            await update.message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝗍𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝖻𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍.")
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
                logger.error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖿𝗈𝗋𝗐𝖺𝗋𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 {user['user_id']}: {e}")
                failure += 1

        await update.message.reply_text(
            f"𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖾.\n𝖲𝗎𝖼𝖼𝖾𝗌𝗌: {success}\n𝖥𝖺𝗂𝗅𝗎𝗋𝖾: {failure}"
        )
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")

async def reply_to_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message_text = update.message.text.lower()
        for filter_doc in filters_collection.find():
            if filter_doc["keyword"] in message_text:
                reply_text = f'<b><i><a href="{filter_doc["link"]}">{filter_doc["text"]}</a></i></b>'
                button1 = InlineKeyboardButton("⌯ 𝖶𝖺𝗍𝖼𝗁 𝖭𝗈𝗐 ⌯", url=filter_doc["link"])
                button2 = InlineKeyboardButton("⌯ 𝖡𝖺𝖼𝗄𝗎𝗉 ⌯", url=BACKUP_CHANNEL)
                reply_markup = InlineKeyboardMarkup([[button1, button2]])
                await update.message.reply_text(
                    reply_text,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                break
    except Exception as e:
        logger.error(f"Error in reply_to_keyword: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        help_text = """
🤖 <b>Bot Commands:</b>

• <code>/start</code> - Start the bot
• <code>/listfilters</code> - List all filters
• <code>/help</code> - Show this help message

👑 <b>Owner Commands:</b>
• <code>/setfilter</code> - Set new filter
• <code>/removefilter</code> - Remove filter
• <code>/stats</code> - Bot statistics
• <code>/broadcast</code> - Broadcast message

🔍 <b>How to use:</b>
Just type any keyword that has been set by the owner!
        """
        await update.message.reply_text(help_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in help_command: {e}")

def main():
    max_retries = 3
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            print(f"🤖 Starting Telegram Bot (Attempt {attempt + 1}/{max_retries})...")
            
            application = Application.builder().token(API_TOKEN).build()

            # Add handlers
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("listfilters", list_filters))
            application.add_handler(CommandHandler("setfilter", set_filter))
            application.add_handler(CommandHandler("removefilter", remove_filter))
            application.add_handler(CommandHandler("stats", stats))
            application.add_handler(CommandHandler("broadcast", broadcast))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keyword))

            print("✅ Bot started successfully!")
            
            # Run with better polling settings
            application.run_polling(
                poll_interval=3,
                timeout=30,
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            break
            
        except Exception as e:
            print(f"❌ Bot crashed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Restarting in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("🚫 Max retries reached. Bot stopped permanently.")
                sys.exit(1)

if __name__ == "__main__":
    main()