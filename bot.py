import os
import re
import logging
import urllib.request
import json
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

# সাউন্ড ও পপ-আপ নোটিফিকেশনের জন্য (আপনার Apps Script-এর ডাটা এখানে বসান)
BOT_TOKEN = "8737282880:AAGKl_ufJ9tPnx16TEX29Vvp-cUxml63bT8"
CHAT_ID = "2091678347"
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

# সাউন্ডসহ মেসেজ পাঠানোর ফাংশন
def send_sound_alert():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": "🚨 <b>FCFS AIRDROP ALERT!</b> 🚨\n\nনতুন অফার আপনার বটে ফরোয়ার্ড করা হয়েছে। জলদি চেক করুন!",
        "parse_mode": "HTML"
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print_log(f"সাউন্ড অ্যালার্ম পাঠাতে এরর: {e}")

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def keyword_handler(event):
    if event.is_group or event.is_channel:
        if event.text:
            text = event.text.lower()
            has_keyword = any(keyword in text for keyword in TARGET_KEYWORDS)
            has_fast_number = bool(FAST_PATTERN.search(text))
            
            if has_keyword or has_fast_number:
                is_valid_post = False
                
                if event.is_channel and not event.is_group:
                    is_valid_post = True
                elif event.is_group:
                    if event.sender_id is None or (event.message.fwd_from and event.message.fwd_from.from_id):
                        is_valid_post = True
                    else:
                        try:
                            perms = await client.get_permissions(event.chat_id, event.sender_id)
                            if perms.is_admin or perms.is_creator:
                                is_valid_post = True
                        except Exception:
                            pass 
                
                if is_valid_post:
                    print_log("🎯 এডমিনের টার্গেট পোস্ট পাওয়া গেছে! মেসেজ ফরোয়ার্ড করা হচ্ছে...")
                    try:
                        # ১. আসল পোস্টটি বটে ফরোয়ার্ড করা হলো (বিনা সাউন্ডে)
                        await event.forward_to(DESTINATION_BOT)
                        
                        # ২. সাউন্ড এবং পপ-আপের জন্য Bot API দিয়ে অ্যালার্ম পাঠানো হলো
                        send_sound_alert()
                        
                        print_log("✅ বটের কাছে মেসেজ ও সাউন্ড অ্যালার্ম পাঠানো সফল হয়েছে!")
                    except Exception as e:
                        print_log(f"❌ মেসেজ পাঠাতে সমস্যা: {e}")
                else:
                    print_log("🚫 সাধারণ মেম্বারের মেসেজ ইগনোর করা হয়েছে।")

async def main():
    print_log("⏳ Render-এর পুরোনো সার্ভার পুরোপুরি বন্ধ হওয়ার জন্য ৩০ সেকেন্ড অপেক্ষা করা হচ্ছে...")
    await asyncio.sleep(30)
    
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
    Thread(target=run_server).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print_log(f"Error: {e}")
