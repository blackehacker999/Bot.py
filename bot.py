#!/usr/bin/env python3
# ===========================================
# Instagram Info Bot (Advanced Version)
# Author: Black Devil [CyberAmarjit]
# ===========================================

import os
import requests
import instaloader
import telebot
from telebot import types

# ============================
# Load Telegram Bot Token
# ============================
TOKEN_FILE = "token.txt"
if not os.path.exists(TOKEN_FILE):
    print("❌ token.txt file missing! Please create and add your bot token.")
    exit()

with open(TOKEN_FILE, "r") as file:
    BOT_TOKEN = file.read().strip()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
loader = instaloader.Instaloader()

print("🤖 Telegram Bot Started Successfully!")

# ============================
# Helper: Fetch Instagram Data
# ============================
def fetch_instagram_profile(username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        return profile
    except Exception as e:
        return str(e)

# ============================
# /start and /help Command
# ============================
@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    text = (
        "👋 *Welcome to Instagram Info Bot*\n\n"
        "Just send me an Instagram username and I will give you detailed information.\n\n"
        "Commands:\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this message\n\n"
        "✨ *Created by* [CyberAmarjit](https://github.com/CyberAmarjit)"
    )
    bot.send_message(message.chat.id, text, disable_web_page_preview=True)

# ============================
# Main Handler for User Input
# ============================
@bot.message_handler(func=lambda msg: True)
def get_instagram_info(message):
    username = message.text.strip().replace("@", "")
    loading = bot.send_message(message.chat.id, f"⏳ Fetching data for `{username}`...")

    profile = fetch_instagram_profile(username)

    # Agar profile object nahi mila to error dikhaye
    if isinstance(profile, str):
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=loading.message_id,
            text=f"❌ Error fetching data for *{username}*\nError: `{profile}`"
        )
        return

    try:
        # ============================
        # Profile Basic Info
        # ============================
        info_text = (
            f"📸 *Instagram Profile Info*\n\n"
            f"👤 *Username:* `{profile.username}`\n"
            f"📝 *Full Name:* `{profile.full_name}`\n"
            f"🆔 *Instagram ID:* `{profile.userid}`\n"
            f"📖 *Bio:* `{profile.biography if profile.biography else 'N/A'}`\n"
            f"🌍 *Website:* {profile.external_url if profile.external_url else 'N/A'}\n\n"
            f"📸 *Posts:* `{profile.mediacount}`\n"
            f"🔔 *Followers:* `{profile.followers}`\n"
            f"🔗 *Following:* `{profile.followees}`\n\n"
            f"👥 *Private Account:* {'Yes 🔒' if profile.is_private else 'No 🔓'}\n"
            f"✅ *Verified:* {'Yes ✅' if profile.is_verified else 'No ❌'}\n"
            f"\n✨ *Created by* [CyberAmarjit](https://github.com/CyberAmarjit)"
        )

        # ============================
        # Download Profile Picture
        # ============================
        profile_pic_url = profile.profile_pic_url
        pic_response = requests.get(profile_pic_url, stream=True)

        photo_path = f"{username}_profile_pic.jpg"
        with open(photo_path, 'wb') as file:
            for chunk in pic_response.iter_content(1024):
                file.write(chunk)

        # ============================
        # Inline Buttons
        # ============================
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🌐 Open Profile", url=f"https://instagram.com/{username}"))
        markup.add(types.InlineKeyboardButton("Download Profile Picture", callback_data=f"download_{username}"))

        # Update loading message with photo + caption
        with open(photo_path, 'rb') as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=info_text,
                reply_markup=markup
            )

        # Delete local file
        os.remove(photo_path)

        # Delete loading message
        bot.delete_message(message.chat.id, loading.message_id)

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=loading.message_id,
            text=f"❌ Error occurred while processing `{username}`.\nError: `{e}`"
        )

# ============================
# Callback Handler for Inline Buttons
# ============================
@bot.callback_query_handler(func=lambda call: call.data.startswith("download_"))
def send_full_profile_pic(call):
    username = call.data.split("_")[1]
    profile = fetch_instagram_profile(username)

    if isinstance(profile, str):
        bot.answer_callback_query(call.id, "❌ Could not fetch profile picture.")
        return

    try:
        profile_pic_url = profile.profile_pic_url
        pic_response = requests.get(profile_pic_url, stream=True)

        photo_path = f"{username}_HD_profile.jpg"
        with open(photo_path, 'wb') as file:
            for chunk in pic_response.iter_content(1024):
                file.write(chunk)

        with open(photo_path, 'rb') as photo:
            bot.send_document(call.message.chat.id, photo, caption=f"🎁 *HD Profile Picture of* `{username}`", parse_mode="Markdown")

        os.remove(photo_path)
        bot.answer_callback_query(call.id, "✅ HD Profile Picture Sent!")

    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Error: {e}")

# ============================
# Start Bot
# ============================
if __name__ == '__main__':
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
