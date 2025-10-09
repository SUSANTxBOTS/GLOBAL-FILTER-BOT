from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from pymongo import MongoClient
import time
import sys
import os
#fill the variables ////////////////////////////////////////////////////////////
API_TOKEN = os.getenv('BOT_TOKEN', '7704955106:AAFEJKG0O2sONGaR6ZQNnRSwZ79sYqOriIc')
MONGO_URI = os.getenv('MONGO_URI', "mongodb+srv://herukosupplier_db_user:ZwLZCi4O46uic1Wv@cluster0.k0d7xeb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
TMDB_API_KEY = "371c10909d11f866a3a1786e3a43cd8e"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
OWNER_IDS = [8156708830, 7125448912, 987654321, 7968389767, 8085299659]
BACKUP_CHANNEL = "https://t.me/+zSzt4s9xq_ZmZWZl"
BOT_CHANNEL = "https://t.me/ThronexCodex"
#///////////////////////////////////////////////////////////////////////////////
try:
    import requests
    TMDB_AVAILABLE = True
except ImportError:
    TMDB_AVAILABLE = False

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000, socketTimeoutMS=10000)
    client.admin.command('ping')
    db = client["xAkairo"]
    filters_collection = db["filters"]
    users_collection = db["users"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def search_tmdb(query):
    if not TMDB_AVAILABLE:
        return {'success': False, 'error': 'TMDB not available'}
    
    try:
        search_url = f"{TMDB_BASE_URL}/search/multi"
        params = {
            'api_key': TMDB_API_KEY,
            'query': query,
            'language': 'en-US',
            'page': 1
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                result = data['results'][0]
                
                media_type = result.get('media_type', 'movie')
                title = result.get('title') or result.get('name', 'N/A')
                overview = result.get('overview', 'No overview available.')
                backdrop_path = result.get('backdrop_path')
                release_date = result.get('release_date') or result.get('first_air_date', 'N/A')
                vote_average = result.get('vote_average', 'N/A')
                
                backdrop_url = f"https://image.tmdb.org/t/p/w780{backdrop_path}" if backdrop_path else None
                
                return {
                    'success': True,
                    'title': title,
                    'overview': overview,
                    'backdrop_url': backdrop_url,
                    'media_type': media_type,
                    'release_date': release_date,
                    'rating': vote_average
                }
        
        return {'success': False, 'error': 'No results found'}
        
    except Exception as e:
        logger.error(f"TMDB search error: {e}")
        return {'success': False, 'error': str(e)}

async def get_anime_info(query):
    if not TMDB_AVAILABLE:
        return {'success': False, 'error': 'TMDB not available'}
    
    try:
        tmdb_data = await search_tmdb(query)
        if not tmdb_data['success']:
            return tmdb_data
        
        title = tmdb_data['title']
        overview = tmdb_data['overview']
        media_type = tmdb_data['media_type']
        release_date = tmdb_data['release_date']
        backdrop_url = tmdb_data['backdrop_url']
        
        if media_type == 'tv':
            caption = (
                f"<b>🎬 𝖲𝗁𝗈𝗐: {title}</b>\n"
                f"<b>📅 𝖲𝖾𝖺𝗌𝗈𝗇: 01</b>\n"
                f"<b>⭐ 𝖦𝖾𝗇𝗋𝖾𝗌: Animation | Action & Adventure | Drama</b>\n"
                f"<b>🔊 𝖠𝗎𝖽𝗂𝗈: 𝖧𝗂𝗇𝖽𝗂 | #𝖮𝖿𝖿𝗂𝖼𝗂𝖺𝗅</b>\n\n"
                f"<b>📝 𝖲𝗒𝗇𝗈𝗉𝗌𝗂𝗌: <i>{overview}</i>..</b>\n"
                
            )
        else:
            year = release_date[:4] if release_date != 'N/A' else 'N/A'
            caption = (
                f"<b>🎬 𝖬𝗈𝗏𝗂𝖾: {title}</b>\n"
                f"<b>📅 𝖸𝖾𝖺𝗋: {year}</b>\n"
                f"<b>🎗 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇: 1h 46min</b>\n"
                f"<b>⭐ 𝖦𝖾𝗇𝗋𝖾𝗌: Animation | Romance | Drama</b>\n"
                f"<b>🔊 𝖠𝗎𝖽𝗂𝗈: 𝖧𝗂𝗇𝖽𝗂 | #𝖮𝖿𝖿𝗂𝖼𝗂𝖺𝗅</b>\n\n"
                f"<b>📝 𝖲𝗒𝗇𝗈𝗉𝗌𝗂𝗌: <i>{overview}</i>..</b>\n"
                
            )
        
        return {
            'success': True,
            'caption': caption,
            'backdrop_url': backdrop_url,
            'media_type': media_type
        }
        
    except Exception as e:
        logger.error(f"Anime info error: {e}")
        return {'success': False, 'error': str(e)}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        
        users_collection.update_one(
            {"user_id": user.id},
            {
                "$setOnInsert": {
                    "user_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "joined_date": time.time()
                }
            },
            upsert=True
        )
        
        image_url = "https://files.catbox.moe/vqomxt.jpg"
        mention = f'<a href="tg://openmessage?user_id={user.id}">{user.first_name}</a>'
        
        caption = (
            f"<b>𝖧𝖾𝗅𝗅𝗈 {mention}, 𝖭𝗂𝖼𝖾 𝗍𝗈 𝗆𝖾𝖾𝗍 𝗒𝗈𝗎 💌</b>\n"
            "<b>𝖨 𝖺𝗆 𝖺 𝖼𝗎𝗌𝗍𝗈𝗆 𝖻𝗈𝗍 𝗆𝖺𝖽𝖾 𝖿𝗈𝗋 𝗍𝖾𝖺𝗆... 𝖮𝗋𝖻𝗂𝗇𝖾𝗑𝖷</b>\n"
            '<b>❖ 𝖯𝗈𝗐𝖾𝗋𝖾𝖽 𝖻𝗒  :- <a href="https://t.me/xAkairo">𝖠𝗄𝖺𝗂𝗋𝗈 𝖩𝗈𝗋𝖾𝗇 !!</a></b>'
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
        try:
            await update.message.reply_text(
                "🤖 <b>Global Filter Bot</b>\n\n"
                "🔹 <b>Developer:</b> @xAkairo\n"
                "🔹 <b>Support:</b> @Thronex_Chats\n"
                "🔹 <b>Channel:</b> @ThronexCodex\n\n"
                "<i>Use /help to see all commands</i>",
                parse_mode="HTML"
            )
        except:
            pass

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
            {"$set": {"text": text, "link": link, "added_by": update.effective_user.id, "added_date": time.time()}},
            upsert=True
        )
        await update.message.reply_text(f"𝖥𝗂𝗅𝗍𝖾𝗋 𝗌𝖾𝗍 𝖿𝗈𝗋 𝗄𝖾𝗒𝗐𝗈𝗋𝖽 '{keyword_lower}'.")
    except Exception as e:
        logger.error(f"Error in set_filter: {e}")
        await update.message.reply_text("❌ An error occurred while setting filter.")

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
        await update.message.reply_text("❌ An error occurred while removing filter.")

async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        filters_cursor = filters_collection.find().sort("keyword", 1)
        filters_list = []
        
        for doc in filters_cursor:
            filters_list.append(f"• {doc['keyword']} → {doc['text']}")
        
        if filters_list:
            message_text = "🔍 <b>Current Filters:</b>\n\n" + "\n".join(filters_list)
            if len(message_text) > 4096:
                parts = [message_text[i:i+4096] for i in range(0, len(message_text), 4096)]
                for part in parts:
                    await update.message.reply_text(part, parse_mode="HTML")
            else:
                await update.message.reply_text(message_text, parse_mode="HTML")
        else:
            await update.message.reply_text("𝖭𝗈 𝖿𝗂𝗅𝗍𝖾𝗋𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍.")
    except Exception as e:
        logger.error(f"Error in list_filters: {e}")
        await update.message.reply_text("❌ An error occurred while listing filters.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.effective_user.id not in OWNER_IDS:
            await update.message.reply_text("𝖳𝖾𝗋𝖺 𝖯𝖺𝗉𝖺 @𝗑𝖥𝗅𝖾𝗑𝗒𝗒 𝖪𝗈 𝖡𝗈𝗅 𝖠𝖽𝖽 𝖪𝖺𝗋 𝖣𝖾𝗀𝖺")
            return

        user_count = users_collection.count_documents({})
        filter_count = filters_collection.count_documents({})
        
        stats_text = (
            f"🚧 <b>Bot Statistics</b>\n\n",
            f"👥 <b>Total Users:</b> {user_count}\n",
            f"🔍 <b>Total Filters:</b> {filter_count}\n",
            f"⚡ <b>Bot Status:</b> Online\n",
            f"🔧 <b>Developer:</b> <a href="https://t.me/xAkairo">𝖠𝗄𝖺𝗂𝗋𝗈 𝖩𝗈𝗋𝖾𝗇 !!</a></b>",
        )
        
        await update.message.reply_text(stats_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in stats: {e}")
        await update.message.reply_text("❌ An error occurred while fetching stats.")

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
        
        progress_msg = await update.message.reply_text(f"📤 𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍𝗂𝗇𝗀... 0/{len(users)}")

        for user in users:
            try:
                await context.bot.forward_message(
                    chat_id=user["user_id"],
                    from_chat_id=from_chat_id,
                    message_id=message_id
                )
                success += 1
                
                if success % 10 == 0:
                    await progress_msg.edit_text(f"📤 𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍𝗂𝗇𝗀... {success}/{len(users)}")
                    
            except Exception as e:
                logger.error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖿𝗈𝗋𝗐𝖺𝗋𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 {user['user_id']}: {e}")
                failure += 1

        await progress_msg.delete()
        await update.message.reply_text(
            f"<b><i>✅ Broadcast Complete</i></b>\n\n"
            f"✓ Success: {success}\n"
            f"✗ Failure: {failure}\n"
            f"📊 Total: {len(users)}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await update.message.reply_text("❌ An error occurred during broadcast.")

async def reply_to_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.message.text.startswith('/'):
            return
            
        message_text = update.message.text.lower()
        
        for filter_doc in filters_collection.find():
            keyword = filter_doc["keyword"].lower()
            
            if keyword in message_text or message_text in keyword:
                if TMDB_AVAILABLE:
                    anime_data = await get_anime_info(filter_doc["text"])
                    
                    if anime_data['success']:
                        caption = anime_data['caption']
                        backdrop_url = anime_data['backdrop_url']
                    else:
                        caption = f'<b><i><a href="{filter_doc["link"]}">{filter_doc["text"]}</a></i></b>'
                        backdrop_url = None
                else:
                    caption = f'<b><i><a href="{filter_doc["link"]}">{filter_doc["text"]}</a></i></b>'
                    backdrop_url = None
                
                button1 = InlineKeyboardButton("🝰 𝙒𝙖𝙩𝙘𝙝 𝘼𝙣𝙙 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙 🝰 ", url=filter_doc["link"])
                button2 = InlineKeyboardButton("𝘽𝙖𝙘𝙠𝙐𝙥 ⧉", url=BACKUP_CHANNEL)
                button3 = InlineKeyboardButton("𝘽𝙤𝙩𝙯 🝰", url=BOT_CHANNEL)
                reply_markup = InlineKeyboardMarkup([[button1], [button2, button3]])
                
                if backdrop_url:
                    try:
                        await update.message.reply_photo(
                            photo=backdrop_url,
                            caption=caption,
                            reply_markup=reply_markup,
                            parse_mode="HTML"
                        )
                    except:
                        await update.message.reply_text(
                            caption,
                            reply_markup=reply_markup,
                            parse_mode="HTML",
                            disable_web_page_preview=True
                        )
                else:
                    await update.message.reply_text(
                        caption,
                        reply_markup=reply_markup,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                break
                
    except Exception as e:
        logger.error(f"Error in reply_to_keyword: {e}")

async def tmdb_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not TMDB_AVAILABLE:
            await update.message.reply_text("❌ TMDB feature is currently unavailable.")
            return
            
        if not context.args:
            await update.message.reply_text("𝖴𝗌𝖺𝗀𝖾: /tmdb <movie/series name>")
            return
            
        query = " ".join(context.args)
        await update.message.reply_text(f"🔍 <i>Searching for '{query}' on TMDB...</i>", parse_mode="HTML")
        
        anime_data = await get_anime_info(query)
        
        if anime_data['success']:
            caption = anime_data['caption']
            backdrop_url = anime_data['backdrop_url']
            
            if backdrop_url:
                try:
                    await update.message.reply_photo(
                        photo=backdrop_url,
                        caption=caption,
                        parse_mode="HTML"
                    )
                except:
                    await update.message.reply_text(
                        caption,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
            else:
                await update.message.reply_text(
                    caption,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
        else:
            await update.message.reply_text(f"❌ No results found for '{query}'")
            
    except Exception as e:
        logger.error(f"Error in tmdb_search: {e}")
        await update.message.reply_text("❌ An error occurred while searching TMDB.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        help_text = """
🤖 <b>Bot Commands:</b>

• <code>/start</code> - Start the bot
• <code>/listfilters</code> - List all filters
• <code>/help</code> - Show this help message
• <code>/tmdb</code> - Search movies/series on TMDB

👑 <b>Owner Commands:</b>
• <code>/setfilter</code> - Set new filter
• <code>/removefilter</code> - Remove filter
• <code>/stats</code> - Bot statistics
• <code>/broadcast</code> - Broadcast message

🔍 <b>How to use:</b>
Just type any keyword that has been set by the owner!

🎬 <b>TMDB Feature:</b>
Auto-fetches anime/movie info with professional format!
        """
        await update.message.reply_text(help_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        await update.message.reply_text("❌ An error occurred while showing help.")

def main():
    max_retries = 5
    retry_delay = 15
    
    for attempt in range(max_retries):
        try:
            print(f"🤖 Starting Telegram Bot (Attempt {attempt + 1}/{max_retries})...")
            
            if not API_TOKEN:
                logger.error("❌ BOT_TOKEN not found!")
                sys.exit(1)
            
            application = Application.builder().token(API_TOKEN).build()

            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("listfilters", list_filters))
            application.add_handler(CommandHandler("setfilter", set_filter))
            application.add_handler(CommandHandler("removefilter", remove_filter))
            application.add_handler(CommandHandler("stats", stats))
            application.add_handler(CommandHandler("broadcast", broadcast))
            application.add_handler(CommandHandler("tmdb", tmdb_search))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keyword))

            print("✅ Bot initialized successfully!")
            print("🔧 Starting polling...")
            if TMDB_AVAILABLE:
                print("🎬 TMDB Feature: Enabled")
                print("🖼️  Using Backdrops instead of Posters")
                print("🔍 Partial Keyword Matching: Enabled")
            else:
                print("⚠️  TMDB Feature: Disabled")
            
            application.run_polling(
                poll_interval=3,
                timeout=30,
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            break
            
        except Exception as e:
            logger.error(f"❌ Bot crashed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"🔄 Restarting in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error("🚫 Max retries reached. Bot stopped permanently.")
                sys.exit(1)

if __name__ == "__main__":
    main()
