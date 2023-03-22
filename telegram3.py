import telebot
import pydash as py_
from NameList import NameList
from settings import Settings


class Telegram:
    def __init__(self, setting: Settings = None, nameList: NameList = None, speakCallback=None) -> None:
        if not setting or not nameList:
            raise Exception("Setting and nameList must not be None")
        self.setting = setting
        self.userList = nameList

        self.speakCB = speakCallback if speakCallback is not None else None

        self.bot = telebot.TeleBot(self.setting.read('API_TOKEN'))
        self.setting.setSendMessageCallback(self.bot.send_message)
        self.userList.setSendMessageCallback(self.bot.send_message)
        self.register_handlers()
        self.__initBot()

    def __initBot(self):
        str = f"""-------------------------TTS bot init-------------------------
Allow Others is {self.setting.read('allowOthers')}
TimeOverGap is {self.setting.read('timeOverGap')}
"""
        self.sendMessage(self.setting.read('OwnerList'), str)
        self.bot.infinity_polling()

    def sendMessage(self, chat_id, message):
        if type(chat_id) is list:
            for id in chat_id:
                self.bot.send_message(id, message)
        else:
            self.bot.send_message(chat_id, message)

    def setSpeakCallback(self, speakCallback):
        self.speakCB = speakCallback

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            welcomeStr = f"""
啊赖的Telegram\"代言人\"
只需要吧你想说的话打进来就会被读出来
輸入 /help 顯示簡單指令教程
"""
            self.bot.reply_to(message, welcomeStr)

        @self.bot.message_handler(commands=['help'])
        def sendHelp(message):
            sendMessage = f"""------Public Commands------
/broadcast : 廣播訊息(Eg : /broadcast 訊息)
"""
            if self.setting.isAdmin(message.from_user.id):
                adminMessage = f"""-----ADMIN PANEL-----
--General Commands--
/allowOther : 其他人使用开关（{self.setting.read('allowOthers')})
/setTimeOverGap : 同一个人重复发言时间间隔（{self.setting.read('timeOverGap')})
/setMaxCharacterAllow : 設定最長可語音長度（{self.setting.read('MaxCharacterAllow')})
/clearMessage : 清除目前所有在佇咧中的語音
/allowNewUser : 允许新用户开关 ({self.setting.read("allowNewUser")})
--User Management--
/getNameList : 取得目前可以發言名單
/addSpeaker : 新增可以發言使用者(Ex : /addSpeaker 123456 name)
/removeSpeaker : 刪除可以發言使用者(Ex : /removeSpeaker 123456)
"""
                sendMessage += adminMessage
            self.bot.reply_to(message, sendMessage)

        @self.bot.message_handler(func=lambda message: True)
        @self.userList.checkUserValid()
        def handle_all_message(message):
            if py_.get(message, "text")[0] == "/":
                self.bot.reply_to(message, "指令錯誤，請輸入 /help 查看指令教程")
            else:
                id = str(py_.get(message, "from_user.id"))
                name = py_.get(self.userList.read(), id)
                txt = f"{name} : {message.text}"
                filteredOwnerList = py_.remove(self.setting.read('OwnerList'), lambda x: x != message.from_user.id)
                self.sendMessage(filteredOwnerList, txt)
                print(txt)
                if self.speakCB is not None:
                    self.speakCB(message)
                else:
                    self.sendMessage(self.setting.read(
                        'OwnerList'), "No speak callback")
