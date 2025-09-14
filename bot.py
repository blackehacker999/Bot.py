import telebot
from telebot.types import ChatPermissions

TOKEN = "7578549309:AAHYLtOixQQCkQcCKH3ZCozXz9ySb-w1csg"
bot = telebot.TeleBot(TOKEN)

# Welcome message
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for new_user in message.new_chat_members:
        bot.reply_to(message, f"Welcome {new_user.first_name}!")

# Auto-ban example: if a user sends a bad word
BAD_WORDS = ["spamword1", "spamword2"]

@bot.message_handler(func=lambda msg: True)
def check_bad_words(message):
    if any(word in message.text.lower() for word in BAD_WORDS):
        bot.delete_message(message.chat.id, message.message_id)
        bot.kick_chat_member(message.chat.id, message.from_user.id)
        bot.send_message(message.chat.id, f"{message.from_user.first_name} was banned for bad language!")

# Auto-mute example
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(
            message.chat.id, user_id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        bot.reply_to(message, f"{message.reply_to_message.from_user.first_name} has been muted!")

# Start the bot
bot.polling()
