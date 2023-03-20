import json
import logging
import os
import time

import pydub
import pydub.playback
import telegram
from telegram.ext import CommandHandler, filters, MessageHandler, Updater


# Settings
class Settings:
    def __init__(self):
        self.file_path = 'setting.json'
        self.data = self.read()

    def read(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def write(self, key, value):
        self.data[key] = value
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)

    def get(self, key):
        return self.data.get(key)


# Configuration
TELEGRAM_TOKEN = Settings().read()['API_TOKEN']
LOG_FILE = 'log.txt'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO
MAX_MESSAGE_LENGTH = 100
ALLOW_OTHERS = False
TARGET_CHANNEL = Settings().read()['Owner']
ADMIN_IDS = Settings().read()['admins']

# Logging


def setup_logging():
    logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


def log_message(message: str):
    logging.info(message)


def log_error(error: str):
    logging.error(error)


# TTS
class TTS:
    def __init__(self):
        self.settings = Settings()
        self.audio = pydub.AudioSegment.from_file('speech.mp3')

    def speak(self, message: telegram.Message):
        try:
            if self.is_allowed(message):
                user_name = message.from_user.first_name
                message_text = f'{user_name} says: {message.text}'
                if len(message_text) > MAX_MESSAGE_LENGTH:
                    log_message(f'Message too long: {message_text}')
                else:
                    audio = self.audio
                    audio.export('temp.mp3', format='mp3')
                    pydub.playback.play(
                        pydub.AudioSegment.from_file('temp.mp3'))
                    os.remove('temp.mp3')
                    log_message(message_text)
        except Exception as e:
            log_error(str(e))

    def is_allowed(self, message: telegram.Message) -> bool:
        if ALLOW_OTHERS:
            return True
        elif message.from_user.id in ADMIN_IDS:
            return True
        else:
            return False

# Telegram


class TelegramBot:
    def __init__(self):
        self.updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.tts = TTS()

    def start(self):
        start_handler = CommandHandler('start', self.start_command)
        self.dispatcher.add_handler(start_handler)

    def speak(self):
        speak_handler = MessageHandler(filters.text & (
            ~filters.command), self.speak_command)
        self.dispatcher.add_handler(speak_handler)

    def messages(self):
        messages_handler = CommandHandler('messages', self.messages_command)
        self.dispatcher.add_handler(messages_handler)

    def allow_others(self):
        allow_others_handler = CommandHandler(
            'allow_others', self.allow_others_command)
        self.dispatcher.add_handler(allow_others_handler)

    def add_admin(self):
        add_admin_handler = CommandHandler('add_admin', self.add_admin_command)
        self.dispatcher.add_handler(add_admin_handler)

    def remove_admin(self):
        remove_admin_handler = CommandHandler(
            'remove_admin', self.remove_admin_command)
        self.dispatcher.add_handler(remove_admin_handler)

    def start_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Welcome to the TTS bot!')

    def speak_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        self.tts.speak(update.message)

    def messages_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        messages = self.get_messages()
        if messages:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='\n'.join(messages))
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='No messages yet')

    def allow_others_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        allow_others = False
        msg = update.message.text.split(" ")
        if len(msg) > 1:
            allow_others = True if msg[1].lower() == "true" else False
        self.settings.write("allow_others", allow_others)
        str = f"allow_others set to {allow_others}"
        context.bot.reply_to(update.message, str)
        log_message(str)

    def add_admin_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            admin_id = int(context.args[0])
            if admin_id not in ADMIN_IDS:
                ADMIN_IDS.append(admin_id)
                self.settings.write("admin_ids", ADMIN_IDS)
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f'Added admin {admin_id}')
                log_message(f'Added admin {admin_id}')
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f'{admin_id} is already an admin')
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='Invalid admin ID')

    def remove_admin_command(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            admin_id = int(context.args[0])
            if admin_id in ADMIN_IDS:
                ADMIN_IDS.remove(admin_id)
                self.settings.write("admin_ids", ADMIN_IDS)
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f'Removed admin {admin_id}')
                log_message(f'Removed admin {admin_id}')
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f'{admin_id} is not an admin')
        except:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='Invalid admin ID')

    def get_messages(self) -> list:
        messages = []
        with open('messages.txt', 'r') as f:
            for line in f:
                messages.append(line.strip())
        return messages

    def send_message(self, message: str):
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TARGET_CHANNEL, text=message)

    def error(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        log_error(f'Update {update} caused error {context.error}')

    def run(self):
        self.start()
        self.speak()
        self.messages()
        self.allow_others()
        self.add_admin()
        self.remove_admin()
        self.dispatcher.add_error_handler(self.error)
        self.updater.start_polling()
        self.updater.idle()


def main():
    setup_logging()
    bot = TelegramBot()
    bot.run()


if __name__ == "__main__":
    main()
