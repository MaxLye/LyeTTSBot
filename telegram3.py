import telebot
from nameList import NameList
from settings import Settings


class Telegram:
    def __init__(self, speakCallback=None) -> None:
        self.setting = Settings('setting.json')
        self.userList = NameList()
        self.lastSpeaker = None
        self.lastSpeakTime = 0

        self.speakCB = speakCallback if speakCallback is not None else None

        self.bot = telebot.TeleBot(self.setting['API_TOKEN'])
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            welcomeStr = """
            啊赖的Telegram\"代言人\"
            """
            self.bot.reply_to(message, welcomeStr)

        @self.bot.message_handler(commands=['help'])
        def sendHelp(message):
            sendMessage = ""
            spotifyMessage = None
            if self.setting.read("SpotifyEnabled"):
                sendMessage += spotifyMessage
            if self.userList(message):
                adminMessage = f"""-----ADMIN PANEL-----
        """
                sendMessage += adminMessage
            self.bot.reply_to(message, sendMessage)
