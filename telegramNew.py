import tts
import json
import time
import telebot
import numbers
import spotipyClient
from pydash import py_

def readSetting():
    with open('setting.json', "r") as f:
        data = json.loads(f.read())
        return data

def writeSetting(key, value):
    data = readSetting()
    print("Write setting {} with {}".format(key, value))
    data[key] = value
    with open('setting.json', 'w') as f:
        json.dump(data, f)

API_TOKEN = readSetting()['API_TOKEN']
LYE_ID = readSetting()['Owner']
bot = telebot.TeleBot(API_TOKEN)
lastSpeaker = None
lastSpeakTime = 0
speakArr = []
speaking = False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcomeStr = """
啊赖的Telegram\"代言人\"
只需要吧你想说的话打进来就会被读出来
輸入 /help 顯示簡單指令教程
    """
    bot.reply_to(message, welcomeStr)

@bot.message_handler(commands=['help'])
def sendHelp(message):
    sendMessage = ""
    spotifyMessage = f"""
--Spotify--
/addSong : 加入歌曲(Eg : /addSong https://open.spotify.com/track/4AvSfXWXhyX6jbSjftXnGD?si=2e0345dd42844024)
"""
    if readSetting()["SpotifyEnabled"]:
        sendMessage += spotifyMessage
    if checkIsAdmin(message):
        adminMessage = f"""-----ADMIN PANEL-----
--General Commands--
/allowOther : 其他人使用开关（{readSetting()['allowOthers']}）
/setTimeOverGap ： 同一个人重复发言时间间隔（{readSetting()['timeOverGap']}）
/setMaxCharacterAllow : 設定最長可語音長度（{readSetting()['MaxCharacterAllow']}）
/clearMessage : 清除目前所有在佇咧中的語音
/broadcast : 廣播訊息(Eg : /broadcast 訊息)
--User Management--
/getNameList : 取得目前可以發言名單
/addSpeaker : 新增可以發言使用者(Ex : /addSpeaker 123456 name)
/removeSpeaker : 刪除可以發言使用者(Ex : /removeSpeaker 123456)
"""
        sendMessage += adminMessage
    bot.reply_to(message, sendMessage)

@bot.message_handler(commands=['allowOther', "allowOthers"])
def allowOther(message):
    if checkIsAdmin(message):
        allowOthers = False
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1:
            allowOthers = True if msg[1].lower() == "true" else False
        writeSetting("allowOthers", allowOthers)
        str = f"allowOthers set to {allowOthers}"
        bot.reply_to(message, str)
        print(str)

@bot.message_handler(commands=['setTimeOverGap'])
def setTimeOverGap(message):
    if checkIsAdmin(message):
        timeGap = 30000
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1 and isinstance(int(msg[1]), numbers.Number):
            timeGap = int(msg[1])
        writeSetting("timeOverGap", timeGap)
        str = f"timeOverGap set to {timeGap}"
        bot.reply_to(message, str)
        print(str)

@bot.message_handler(commands=['clearMessage'])
def clearMessage(message):
    if checkIsAdmin(message):
        speakArr = []
        bot.reply_to(message,"Message cleared")
        print("Message cleared")

@bot.message_handler(commands=['setMaxCharacterAllow'])
def setMaxCharacterAllow(message):
    if checkIsAdmin(message):
        maxLimit = 100
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1 and isinstance(int(msg[1]), numbers.Number):
            maxLimit = int(msg[1])
        writeSetting("MaxCharacterAllow", maxLimit)
        str = f"MaxCharacterAllow set to {maxLimit}"
        bot.reply_to(message, str)
        print(str)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if checkIsAdmin(message):
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1:
            str = f"Broadcast Message : {msg[1]}"
            for key, value in readNameList().items():
                bot.send_message(key, str)
            print(str)
            bot.reply_to(message, str)

@bot.message_handler(commands=['addSong'])
def addSong(message):
    if readSetting()["SpotifyEnabled"]:
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1:
            spotipyClient.addSong(msg[1])
            str = f"Added song {msg[1]}" 
            print(str)
            bot.reply_to(message, str)
    else:
        str = f"Spotify is not enable for this bot"
        print(str)
        bot.reply_to(message, str)

def checkIsAdmin(message):
    return py_.index_of(readSetting()["admins"], py_.get(message, 'from_user.id')) > -1

@bot.message_handler(commands=['getNameList'])
def getNameList(message):
    if checkIsAdmin(message):
        nameList = ""
        for key, value in readNameList().items():
            nameList += f"{key} : {value}\n"
        bot.reply_to(message,f"{nameList}")

@bot.message_handler(commands=['addSpeaker'])
def addSpeaker(message):
    if checkIsAdmin(message):
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 2 and isinstance(int(msg[1]), numbers.Number):
            str = f"Add user {msg[1]} with name {msg[2]}"
            print(str)
            bot.reply_to(message, str)
            writeNameList(msg[1], msg[2])

@bot.message_handler(commands=['removeSpeaker'])
def removeSpeaker(message):
    if checkIsAdmin(message):
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1 and isinstance(int(msg[1]), numbers.Number):
            str = f"Remove user {msg[1]}"
            print(str)
            bot.reply_to(message, str)
            writeNameList(msg[1])
        pass

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    senderName = getSenderName(py_.get(message, 'from_user'))
    if senderName or readSetting()["allowNewUser"]:
        str = f"{senderName}讲, {py_.get(message, 'text')}"
        if py_.get(message, "from_user.id") != LYE_ID:
            bot.send_message(LYE_ID, str)
        print(str)
        if checkIsAdmin(message) or readSetting()['allowOthers']:
            speakMessage = formatMessage(message)
            if len(speakMessage) > readSetting()["MaxCharacterAllow"]:
                bot.reply_to(message, f"Message exceeded maximum length limit of {readSetting()['MaxCharacterAllow']}")
            else:
                speakArr.append(speakMessage)
                speak()
        else:
            bot.send_message(py_.get(message, "from_user.id"),"Others speaking is not allowed, please contact A-Lye to enable")
    else:
        bot.send_message(py_.get(message, "from_user.id"), "Sorry, you are not allowed to speak on this bot. If this is an error, please contact A-Lye.")

def speak():
    global speaking
    if len(speakArr) and not speaking:
        speaking = True
        msg = speakArr.pop(0)
        tts.speak(msg, speakEnd)

def speakEnd():
    global speaking
    speaking = False
    speak()

def getCurrentTimeStamp():
    return int(round(time.time() * 1000))

def isTimeWithinRange():
    global lastSpeakTime
    return (getCurrentTimeStamp() - lastSpeakTime) < readSetting()['timeOverGap']

def formatMessage(message):
    global lastSpeaker, lastSpeakTime
    name = getSenderName(py_.get(message, "from_user"))
    id = py_.get(message, "from_user.id")
    msg = py_.get(message, "text")
    if not (lastSpeaker == id and isTimeWithinRange()):
        msg = f"{name}讲, {msg}"
    lastSpeaker = py_.get(message, "from_user.id")
    lastSpeakTime = getCurrentTimeStamp()
    return msg

def getSenderName(messageObject):
    name = py_.get(messageObject, "first_name") if readSetting()["allowNewUser"] else None
    id = py_.get(messageObject, "id")
    with open('NameList.json', "r", encoding="utf8") as f:
        data = json.loads(f.read())
        uName = py_.get(data, f"{id}", default = None)
        if uName == None:
            bot.send_message(LYE_ID, f"New User {id} : {name}")
        else:
            name = uName
    return name

def readNameList():
    with open('NameList.json', "r") as f:
        data = json.loads(f.read())
        return data

def writeNameList(id, name = None):
    data = readNameList()
    if name == None:
        py_.unset(data, f"{id}")
    else:
        data[id] = name
    with open('NameList.json', 'w') as f:
        json.dump(data, f)

def initBot():
    str = f"""-------------------------TTS bot init-------------------------
Allow Others is {readSetting()['allowOthers']}
TimeOverGap is {readSetting()['timeOverGap']}
    """
    bot.send_message(LYE_ID, str)

initBot()
bot.infinity_polling()
