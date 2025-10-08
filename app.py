from flask import Flask
import threading
import os
import subprocess
import time

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '𝖳𝗁𝗂𝗌 𝖻𝗈𝗍 𝗂𝗌 𝗆𝖺𝖽𝖾 𝖻𝗒 @𝗑𝖥𝗅𝖾𝗑𝗒𝗒 𝖺𝗇𝖽 𝖼𝗎𝗋𝗋𝖾𝗇𝗍𝗅𝗒 𝗂𝗍 𝗁𝗈𝗌𝗍𝖾𝖽 𝖺𝗇𝖽 𝗅𝗂𝗏𝖾 𝖿𝗈𝗋 𝖾𝗏𝖾𝗋𝗒𝗈𝗇𝖾'

def run_bot():
    while True:
        try:
            print("🤖 Starting Telegram Bot...")
            # Run your bot script
            subprocess.run(["python", "bot.py"])
        except Exception as e:
            print(f"❌ Bot crashed: {e}")
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))