import json
import requests
import time
import urllib
import tts

TOKEN = "5062560075:AAEXxlSbwTemovGJghttYYSkWuBcPBq3Lvs"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
lastSpeaker = None
lastSpeakTime = None

speakEnable = True

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def echo_all(updates):
    global lastSpeaker
    global lastSpeakTime
    for update in updates["result"]:
        if "edited_message" in update:
            update["message"] = update["edited_message"]
        if "text" in update["message"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            name = getSenderName(update["message"]["chat"])
            if chat == 447074722:
                if "entities" in update["message"] and update["message"]["entities"][0]["type"] == "bot_command":
                    processCommand(text)
                else :
                    print(name + "讲," + text)
                    if speakEnable:
                        if lastSpeaker == chat and isTimeWithinRange():
                            tts.speak(text)
                        else:
                            tts.speak(name + "讲," + text)
            else:
                str = "{}({})讲,{}".format(name,chat,text)
                print(str)
                send_message(str, 447074722)
                if speakEnable:
                    if bool(readByKey("allowOthers")):
                        if lastSpeaker == chat and isTimeWithinRange():
                            tts.speak(text)
                        else:
                            tts.speak(name + "讲," + text)
                    else:
                        send_message("Speak is currently not allowed, please contact A-Lye to enable", chat)
            lastSpeaker = chat
            lastSpeakTime = getCurrentTimeStamp()

def processCommand(command):
    command = command.split(" ")
    if command[0] == "/allowOthers":
        allowOthers = False
        if len(command) > 1:
            command[1] = command[1].lower()
            allowOthers = True if command[1] == "true" else False
        writeSetting("allowOthers", allowOthers)
        print("Allow Others set to {}".format(allowOthers))
        send_message("Allow Others set to {}".format(allowOthers), 447074722)
    elif command[0] == "/setTimeOverGap":
        timeOverGap = 30000
        if len(command) > 1:
            timeOverGap = command[1]
        writeSetting("timeOverGap",timeOverGap)
        print("TimeOverGap set to {}".format(timeOverGap))
        send_message("TimeOverGap set to {}".format(timeOverGap), 447074722)

def isTimeWithinRange():
    global lastSpeakTime
    return (getCurrentTimeStamp() - lastSpeakTime) < readByKey("timeOverGap")

def getCurrentTimeStamp():
    return int(round(time.time() * 1000))

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def getSenderName(messageObject):
    name = messageObject['first_name']
    with open('NameList.txt', encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            arr = line.split(':')
            if messageObject["id"] == int(arr[0]):
                name = arr[1].replace('\n','')
    return name

def readSetting():
    with open('setting.json', "r") as f:
        data = json.loads(f.read())
        return data

def readByKey(key):
    return readSetting()[key]

def writeSetting(key, value):
    data = readSetting()
    print("Write setting {} with {}".format(key, value))
    data[key] = value
    with open('setting.json', 'w') as f:
        json.dump(data, f)

def main():
    last_update_id = None
    send_message("-------------------------TTS bot init-------------------------", 447074722)
    send_message("Allow Others is {}".format(readByKey("allowOthers")), 447074722)
    send_message("TimeOverGap is {}".format(readByKey("timeOverGap")), 447074722)
    while True:
        try:
            updates = get_updates(last_update_id)
            if len(updates["result"]) > 0:
                if last_update_id != None:
                    echo_all(updates)
                last_update_id = get_last_update_id(updates) + 1
        except BaseException as err:
            print(err)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
