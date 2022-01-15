import tts
import json
import time
import telebot
import numbers
from pydash import py_

API_TOKEN = '5062560075:AAEXxlSbwTemovGJghttYYSkWuBcPBq3Lvs'
LYE_ID = 447074722
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
    """
    bot.reply_to(message, welcomeStr)

@bot.message_handler(commands=['help'])
def sendHelp(message):
    if checkIsAdmin(message):
        helpMessage = f"""
/allowOther : 其他人使用开关（{readSetting()['allowOthers']}）
/setTimeOverGap ： 同一个人重复发言时间间隔（{readSetting()['timeOverGap']}）
/getNameList : 取得目前可以發言名單
/addSpeaker : 新增可以發言使用者(Ex : /addSpeaker 123456 name)
/removeSpeaker : 刪除可以發言使用者(Ex : /removeSpeaker 123456)
        """
        bot.reply_to(message, helpMessage)

@bot.message_handler(commands=['allowOther', "allowOthers"])
def allowOther(message):
    if checkIsAdmin(message):
        allowOthers = False
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1:
            allowOthers = True if msg[1].lower() == "true" else False
        writeSetting("allowOthers", allowOthers)
        bot.reply_to(message, f"allowOthers set to {allowOthers}")

@bot.message_handler(commands=['setTimeOverGap'])
def setTimeOverGap(message):
    if checkIsAdmin(message):
        timeGap = 30000
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1 and isinstance(int(msg[1]), numbers.Number):
            timeGap = int(msg[1])
        writeSetting("timeOverGap", timeGap)
        bot.reply_to(message, f"timeOverGap set to {timeGap}")

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
            writeNameList(msg[1], msg[2])

@bot.message_handler(commands=['removeSpeaker'])
def removeSpeaker(message):
    if checkIsAdmin(message):
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1 and isinstance(int(msg[1]), numbers.Number):
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
            speakArr.append(formatMessage(message))
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
    name = py_.get(messageObject, "first_name")
    id = py_.get(messageObject, "id")
    with open('NameList.json', "r", encoding="utf8") as f:
        data = json.loads(f.read())
        uName = py_.get(data, f"{id}", default = None)
        if uName == None:
            bot.send_message(LYE_ID, f"New User {id} : {name}")
        else:
            name = uName
    return name

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

def readNameList():
    with open('NameList.json', 'r') as f:
        data = json.loads(f.read())
        return data

def writeNameList(id, name = None):
    data = readNameList()
    if name == None:
        str = f"Remove user {id}"
        print(str)
        bot.send_message(LYE_ID, str)
        py_.unset(data, f"{id}")
    else:
        str = f"Add user {id} with name {name}"
        print(str)
        bot.send_message(LYE_ID, str)
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
