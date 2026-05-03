import os
import re  # নতুন লজিকের জন্য এটি যুক্ত করা হয়েছে
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

# পরিবেশ থেকে ডাটা নেওয়া
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

# -----------------------------------------------------
# সাধারণ কিওয়ার্ডগুলো (এগুলো সরাসরি চেক করবে)
TARGET_KEYWORDS = ['fcfs', 'first come', 'first serve']

# এখানে আপনার বটের ইউজারনেম দিন (অবশ্যই @ সহ)
DESTINATION_BOT = '@my_airdrop_notification_bot'
# -----------------------------------------------------

# ওয়েব সার্ভার
app = Flask(__name__)
@app.route('/')
def home():
    return "Airdrop Bot is Running 24/7 on Render!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

client = TelegramClient(StringSession(session_string), api_id, api_hash)

# 'fast' এর পর সংখ্যা চেক করার লজিক (যেমন: fast 500, fast 10k, fast50)
FAST_PATTERN = re.compile(r'\bfast\s*\d+', re.IGNORECASE)

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def keyword_handler(event):
    if event.is_group or event.is_channel:
        if event.text:
            text = event.text.lower()
            
            # শর্ত ১: সাধারণ কিওয়ার্ডগুলো চেক করা
            has_keyword = any(keyword in text for keyword in TARGET_KEYWORDS)
            
            # শর্ত ২: 'fast' এর পর সংখ্যা আছে কি না চেক করা
            has_fast_number = bool(FAST_PATTERN.search(text))
            
            if has_keyword or has_fast_number:
                print("টার্গেট কিওয়ার্ড বা Fast Number পাওয়া গেছে! বটের কাছে ফরোয়ার্ড করা হচ্ছে...")
                await client.send_message(DESTINATION_BOT, "🚨 **AIRDROP ALERT!** 🚨\n\n**Post:**\n" + event.text)
                await event.forward_to(DESTINATION_BOT)

if __name__ == '__main__':
    Thread(target=run_server).start()
    client.start()
    print("বট সফলভাবে চালু হয়েছে! স্ক্যান চলছে...")
    client.run_until_disconnected()
