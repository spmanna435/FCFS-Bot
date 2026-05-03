import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

# পরিবেশ (Environment) থেকে ডাটা নেওয়া
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

# -----------------------------------------------------
# আপনার কাঙ্ক্ষিত কিওয়ার্ডের লিস্ট (সব ছোট হাতের অক্ষরে লিখবেন)
TARGET_KEYWORDS = ['fcfs', 'first come', 'first serve', 'fast']
# -----------------------------------------------------

# ওয়েব সার্ভার
app = Flask(__name__)
@app.route('/')
def home():
    return "Airdrop Bot is Running 24/7 on Render!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# টেলিগ্রাম বট
client = TelegramClient(StringSession(session_string), api_id, api_hash)

@client.on(events.NewMessage)
async def keyword_handler(event):
    if event.is_group or event.is_channel:
        if event.text:
            text = event.text.lower()
            
            # চেক করবে মেসেজের ভেতর আমাদের লিস্টের কোনো কিওয়ার্ড আছে কি না
            if any(keyword in text for keyword in TARGET_KEYWORDS):
                print("টার্গেট কিওয়ার্ড পাওয়া গেছে! মেসেজ ফরোয়ার্ড করা হচ্ছে...")
                # ফরোয়ার্ড করা
                await client.send_message('me', "🚨 **AIRDROP ALERT!** 🚨\n\n**Post:**\n" + event.text)
                await event.forward_to('me')

if __name__ == '__main__':
    Thread(target=run_server).start()
    client.start()
    print("বট সফলভাবে চালু হয়েছে! স্ক্যান চলছে...")
    client.run_until_disconnected()
