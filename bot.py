#!/usr/bin/env python3
# ===========================================
# Instagram Info Bot with ASCII Banner
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
# ASCII Banner
# ============================
def amarjit_ascii_banner():
    return (
        "```\n"
        "  █████╗ ███╗   ███╗ █████╗ ██████╗      ██╗██╗████████╗\n"
        " ██╔══██╗████╗ ████║██╔══██╗██╔══██╗     ██║██║╚══██╔══╝\n"
        " ███████║██╔████╔██║███████║██████╔╝     ██║██║   ██║   \n"
        " ██╔══██║██║╚██╔╝██║██╔══██║██╔══██╗██   ██║██║   ██║   \n"
        " ██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║╚█████╔╝██║   ██║   \n"
        " ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚════╝ ╚═╝   ╚═╝   \n"
        "```"
    )

# ============================
# /start and /help Command
# ============================
@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    banner = amarjit_ascii_banner()
    text = (
        f"{banner}\n"
        "👋 *Welcome to Instagram Info Bot*\n\n"
        "Just send me an Instagram username and I will fetch **full profile details** for you.\n\n"
        "📖 *Commands:*\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help message\n\n"
        "✨ *Credit by* `AMARJIT`"
    )
    bot.send_message(message.chat.id, text, disable_web_page_preview=True)

# ============================
# Main Handler for Username
# ============================
@bot.message_handler(func=lambda msg: True)
def get_instagram_info(message):
    username = message.text.strip().replace("@", "")
    loading = bot.send_message(message.chat.id, f"⏳ Fetching data for `{username}`...")

    profile = fetch_instagram_profile(username)

    if isinstance(profile, str):
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=loading.message_id,
            text=f"❌ Error fetching data for *{username}*\nError: `{profile}`"
        )
        return

    try:
        # ============================
        # Profile Info with ASCII Banner
        # ============================
        banner = amarjit_ascii_banner()
        info_text = (
            f"{banner}\n\n"
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
            f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ *Credit by* `AMARJIT`"
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
        markup.add(types.InlineKeyboardButton("⬇ Download HD Profile Pic", callback_data=f"download_{username}"))

        with open(photo_path, 'rb') as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=info_text,
                reply_markup=markup
            )

        os.remove(photo_path)
        bot.delete_message(message.chat.id, loading.message_id)

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=loading.message_id,
            text=f"❌ Error occurred while processing `{username}`.\nError: `{e}`"
        )

# ============================
# Fetch Instagram Profile
# ============================
def fetch_instagram_profile(username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        return profile
    except Exception as e:
        return str(e)

# ============================
# Callback Handler for HD Profile Pic
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
            bot.send_document(
                call.message.chat.id,
                photo,
                caption=f"🎁 *HD Profile Picture of* `{username}`\n\n✨ *Credit by* `AMARJIT`",
                parse_mode="Markdown"
            )

        os.remove(photo_path)
        bot.answer_callback_query(call.id, "✅ HD Profile Picture Sent!")

    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Error: {e}")

# ============================
# Start Bot
# ============================
if __name__ == '__main__':
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
