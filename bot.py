import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread
import asyncio

# পরিবেশ থেকে ডাটা নেওয়া
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

# -----------------------------------------------------
TARGET_KEYWORDS = ['fcfs', 'first come', 'first serve']
DESTINATION_BOT = '@my_airdrop_notification_bot' # এখানে আপনার বটের ইউজারনেম দিন
# -----------------------------------------------------

app = Flask(__name__)
@app.route('/')
def home():
    return "Airdrop Bot is Running 24/7 on Render!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

client = TelegramClient(StringSession(session_string), api_id, api_hash)
FAST_PATTERN = re.compile(r'\bfast\s*\d+', re.IGNORECASE)

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def keyword_handler(event):
    if event.is_group or event.is_channel:
        if event.text:
            text = event.text.lower()
            has_keyword = any(keyword in text for keyword in TARGET_KEYWORDS)
            has_fast_number = bool(FAST_PATTERN.search(text))
            
            if has_keyword or has_fast_number:
                print("টার্গেট কিওয়ার্ড পাওয়া গেছে! বটের কাছে ফরোয়ার্ড করা হচ্ছে...")
                try:
                    await client.send_message(DESTINATION_BOT, "🚨 **AIRDROP ALERT!** 🚨\n\n**Post:**\n" + event.text)
                    await event.forward_to(DESTINATION_BOT)
                except Exception as e:
                    print(f"মেসেজ পাঠাতে সমস্যা হয়েছে: {e}")

# নতুন সিস্টেম: যেন বট আটকে না যায়
async def main():
    try:
        print("টেলিগ্রামের সাথে কানেক্ট করার চেষ্টা করা হচ্ছে...")
        await client.connect()
        
        # চেক করবে লগইন ঠিক আছে কি না
        if not await client.is_user_authorized():
            print("❌ ERROR: আপনার Session String কাজ করছে না বা এক্সপায়ার হয়ে গেছে! দয়া করে Colab থেকে নতুন String বানিয়ে Render-এ দিন।")
            return
            
        print("✅ বট সফলভাবে চালু হয়েছে! স্ক্যান চলছে...")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ বড় ধরনের সমস্যা হয়েছে: {e}")

if __name__ == '__main__':
    Thread(target=run_server).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
