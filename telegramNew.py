import time
import telebot
import numbers
import speakControl
import settings
import nameList
from pydash import py_
setting = settings.Settings('setting.json')
nameLists = nameList.NameList()
API_TOKEN = setting.read('API_TOKEN')
LYE_ID = setting.read('Owner')
bot = telebot.TeleBot(API_TOKEN)
lastSpeaker = None
lastSpeakTime = 0
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcomeStr = """
啊赖的Telegram\"代言人\"
    """
    bot.reply_to(message, welcomeStr)
@bot.message_handler(commands=['help'])
def sendHelp(message):
    sendMessage = ""
    spotifyMessage = f"""
--Spotify--
"""
    if setting.read("SpotifyEnabled"):
        sendMessage += spotifyMessage
    if checkIsAdmin(message):
        adminMessage = f"""-----ADMIN PANEL-----
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
        setting.write("allowOthers", allowOthers)
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
        setting.write("timeOverGap", timeGap)
        str = f"timeOverGap set to {timeGap}"
        bot.reply_to(message, str)
        print(str)
@bot.message_handler(commands=['allowNewUser'])
def allowNewUser(message):
    if checkIsAdmin(message):
        allowNewUserSpeak = False
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1:
            allowNewUserSpeak = True if msg[1].lower() == "true" else False
        setting.write("allowNewUser", allowNewUserSpeak)
        str = f"allowNewUserSpeak set to {allowNewUserSpeak}"
        bot.reply_to(message, str)
        print(str)
@bot.message_handler(commands=['clearMessage'])
def clearMessage(message):
    if checkIsAdmin(message):
        bot.reply_to(message, "Message cleared")
        print("Message cleared")
@bot.message_handler(commands=['setMaxCharacterAllow'])
def setMaxCharacterAllow(message):
    if checkIsAdmin(message):
        maxLimit = 100
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1 and isinstance(int(msg[1]), numbers.Number):
            maxLimit = int(msg[1])
        setting.write("MaxCharacterAllow", maxLimit)
        str = f"MaxCharacterAllow set to {maxLimit}"
        bot.reply_to(message, str)
        print(str)
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if checkIsAdmin(message):
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1:
            str = f"Broadcast Message : {msg[1]}"
            for key, value in nameLists.read():
                bot.send_message(key, str)
            print(str)
            bot.reply_to(message, str)
@bot.message_handler(commands=['addSong', 'addsong'])
def addSong(message):
    if setting.read("SpotifyEnabled"):
        msg = py_.get(message, "text").split(" ")
        senderName = getSenderName(py_.get(message, 'from_user'))
        if len(msg) > 1:
            spotipyClient.addSong(msg[1])
            str = f"Added song {msg[1]}"
            print(str)
            bot.reply_to(message, str)
            bot.send_message(LYE_ID, f"{senderName} {str}")
    else:
        str = f"Spotify is not enable for this bot"
        print(str)
        bot.reply_to(message, str)
@bot.message_handler(commands=['getCurrentSong', 'getcurrentsong'])
def getCurrentSong(message):
    if setting.read("SpotifyEnabled"):
        playListStr = spotipyClient.getCurrentPlayingSong()
        bot.reply_to(message, playListStr)
    else:
        str = f"Spotify is not enable for this bot"
        print(str)
        bot.reply_to(message, str)
def checkIsAdmin(message):
    return py_.index_of(setting.read("admins"), py_.get(message, 'from_user.id')) > -1
@bot.message_handler(commands=['getNameList'])
def getNameList(message):
    if checkIsAdmin(message):
        nameList = ""
        for key, value in nameLists.read():
            nameList += f"{key} : {value}\n"
        bot.reply_to(message, f"{nameList}")
@bot.message_handler(commands=['addSpeaker'])
def addSpeaker(message):
    if checkIsAdmin(message):
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 2 and isinstance(int(msg[1]), numbers.Number):
            str = f"Add user {msg[1]} with name {msg[2]}"
            print(str)
            bot.reply_to(message, str)
            nameLists.write(msg[1], msg[2])
@bot.message_handler(commands=['removeSpeaker'])
def removeSpeaker(message):
    if checkIsAdmin(message):
        msg = py_.get(message, "text").split(" ")
        if len(msg) > 1 and isinstance(int(msg[1]), numbers.Number):
            str = f"Remove user {msg[1]}"
            print(str)
            bot.reply_to(message, str)
            nameLists.write(msg[1])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    senderName = getSenderName(py_.get(message, 'from_user'))
    if senderName or setting.read("allowNewUser"):
        str = f"{senderName}讲, {py_.get(message, 'text')}"
        if py_.get(message, 'text')[0] == "/":
            bot.reply_to(message, "Command error")
        else:
            if py_.get(message, "from_user.id") != LYE_ID:
                bot.send_message(LYE_ID, str)
            print(str)
            if checkIsAdmin(message) or setting.read('allowOthers'):
                speakMessage = formatMessage(message)
                if len(speakMessage) > setting.read("MaxCharacterAllow"):
                    bot.reply_to(
                        message, f"Message exceeded maximum length limit of {setting.read('MaxCharacterAllow')}")
                else:
                    speakControl.speak(speakMessage)
            else:
                bot.send_message(py_.get(message, "from_user.id"),"Others speaking is not allowed, please contact A-Lye to enable")
    else:
        bot.send_message(py_.get(message, "from_user.id"),"Sorry, you are not allowed to speak on this bot. If this is an error, please contact A-Lye.")
def getCurrentTimeStamp():
    return int(round(time.time() * 1000))
def isTimeWithinRange():
    global lastSpeakTime
    return (getCurrentTimeStamp() - lastSpeakTime) < setting.read('timeOverGap')
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
    name = py_.get(messageObject, "first_name") if setting.read("allowNewUser") else None
    id = py_.get(messageObject, "id")
    uName = py_.get(nameLists.read(), f"{id}", default=None)
    if uName == None:
        bot.send_message(LYE_ID, f"New User {id} : {name}")
    else:
        name = uName
    return name
def initBot():
    str = f"""-------------------------TTS bot init-------------------------
Allow Others is {setting.read('allowOthers')}
TimeOverGap is {setting.read('timeOverGap')}
    """
    bot.send_message(LYE_ID, str)


initBot()
bot.infinity_polling()
