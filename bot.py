import os
import re
import logging
import unicodedata
import hashlib  # মেসেজের টেক্সট চেনার জন্য
import time     # সময় ট্র্যাক করার জন্য
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from flask import Flask
from threading import Thread
import asyncio

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

# -----------------------------------------------------
TARGET_KEYWORDS = ['fcfs', 'first come', 'first serve', 'free claim' , 'verified x' , 'x premium' , 'free nft' , 'public mint' , 'nft mint' , 'nft minting' , 'verified twitter' , 'twitter premium' , 'farcaster users' , 'farcaster user' , 'giveaway', 'exchange airdrop' , 'instant free' , 'instant claim' , 'exchange offer' , 'wallet airdrop' , 'wallet offer' , 'limited']
FORWARD_GROUP = '@instantfcfsairdrop'
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
FAST_PATTERN = re.compile(r'\b\d+[\d,\.]*\s*(?:\$|usd|usdt|bnb|eth|btc|usdc|sol|b|k|m)?\s*\b(first|instant|claim|free)\b|\b(first|instant|claim|free)\b\s*(?:\$|€)?\s*\d+', re.IGNORECASE)

# --- নতুন বুলেটপ্রুফ মেমরি সিস্টেম (মেসেজ টেক্সট + টাইম) ---
recent_messages = {}

async def safe_forward(event):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await asyncio.sleep(1) 
            await event.forward_to(FORWARD_GROUP)
            print_log("✅ গ্রুপে মেসেজ ফরোয়ার্ড সফল হয়েছে!")
            return 
        except FloodWaitError as e:
            print_log(f"⚠️ টেলিগ্রাম স্প্যাম লিমিট! {e.seconds} সেকেন্ড অপেক্ষা...")
            await asyncio.sleep(e.seconds + 1)
        except Exception as e:
            print_log(f"❌ ফরোয়ার্ড করতে সমস্যা: {e}, আবার চেষ্টা করা হচ্ছে...")
            await asyncio.sleep(2)

async def process_message(event):
    if event.is_group or event.is_channel:
        if event.raw_text:
            
            # ১. মেসেজের একটি ইউনিক ফিঙ্গারপ্রিন্ট বানানো হলো (লেখার ওপর ভিত্তি করে)
            msg_hash = hashlib.md5(event.raw_text.encode('utf-8')).hexdigest()
            current_time = time.time()
            
            # ২. চেক করা হচ্ছে এই একই লেখা গত ১০ মিনিট (৬০০ সেকেন্ড) এর মধ্যে ফরোয়ার্ড হয়েছে কি না
            if msg_hash in recent_messages:
                if current_time - recent_messages[msg_hash] < 600:
                    print_log("⚠️ একই মেসেজ বারবার আসছে। ডাবল ফরোয়ার্ড ব্লক করা হলো!")
                    return
            
            normal_text = unicodedata.normalize('NFKC', event.raw_text)
            text = normal_text.lower()
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
                    print_log("🎯 এডমিনের টার্গেট পোস্ট পাওয়া গেছে! গ্রুপে ফরোয়ার্ড করা হচ্ছে...")
                    # ৩. মেসেজ ফরোয়ার্ড করার পর মেমরিতে সেভ করে রাখা হলো
                    recent_messages[msg_hash] = current_time
                    await safe_forward(event)

# শুধু নতুন মেসেজ ধরবে
@client.on(events.NewMessage(incoming=True, outgoing=True))
async def on_new_message(event):
    await process_message(event)

async def main():
    print_log("⏳ Render-এর পুরোনো সার্ভার পুরোপুরি বন্ধ হওয়ার জন্য ৩০ সেকেন্ড অপেক্ষা করা হচ্ছে...")
    await asyncio.sleep(30)
    
    print_log("🔄 টেলিগ্রামের সাথে কানেক্ট করার চেষ্টা করা হচ্ছে...")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print_log("❌ ERROR: আপনার Session String কাজ করছে না!")
            return
            
        print_log("✅ স্ক্যানার বট সফলভাবে চালু হয়েছে! স্ক্যান চলছে...")
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
