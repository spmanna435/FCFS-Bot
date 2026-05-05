import os
import re
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread
import asyncio

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

# -----------------------------------------------------
TARGET_KEYWORDS = ['fcfs', 'first come', 'first serve', 'farcaster users' , 'farcaster user' , 'giveaway', 'exchange airdrop' , 'instant free' , 'exchange offer' , 'wallet airdrop' , 'wallet offer' , 'limited']
DESTINATION_BOT = '@my_airdrop_notification_bot' 
# -----------------------------------------------------

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return "Bot is Running!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def print_log(msg):
    print(msg, flush=True)

client = TelegramClient(StringSession(session_string), api_id, api_hash)
FAST_PATTERN = re.compile(r'\b(fast|first|instant|claim)\s*\d+', re.IGNORECASE)

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def keyword_handler(event):
    if event.is_group or event.is_channel:
        if event.text:
            text = event.text.lower()
            has_keyword = any(keyword in text for keyword in TARGET_KEYWORDS)
            has_fast_number = bool(FAST_PATTERN.search(text))
            
            if has_keyword or has_fast_number:
                print_log("🎯 টার্গেট কিওয়ার্ড পাওয়া গেছে! বটের কাছে মেসেজ ফরোয়ার্ড করা হচ্ছে...")
                try:
                    await client.send_message(DESTINATION_BOT, "🚨 **AIRDROP ALERT!** 🚨\n\n**Post:**\n" + event.text)
                    await event.forward_to(DESTINATION_BOT)
                    print_log("✅ বটের কাছে মেসেজ পাঠানো সফল হয়েছে!")
                except Exception as e:
                    print_log(f"❌ মেসেজ পাঠাতে সমস্যা: {e}")

async def main():
    print_log("🔄 টেলিগ্রামের সাথে কানেক্ট করার চেষ্টা করা হচ্ছে...")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print_log("❌ ERROR: আপনার Session String কাজ করছে না!")
            return
            
        print_log("✅ বট সফলভাবে চালু হয়েছে! স্ক্যান চলছে...")
        await client.run_until_disconnected()
    except Exception as e:
        print_log(f"❌ সমস্যা হয়েছে: {e}")

if __name__ == '__main__':
    # ওয়েব সার্ভার চালু
    Thread(target=run_server).start()
    
    # নতুন Python ভার্সনের জন্য Event Loop ফিক্স
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print_log(f"Error: {e}")
