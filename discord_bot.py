import os
import time
import json
import discord
import speakControl
from pydash import py_
from dotenv import load_dotenv

load_dotenv(dotenv_path="discord.env")
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
LOG_CHANNEL = os.getenv('DISCORD_SERVER_LOG_CHANNEL')

client = discord.Client()
lastSpeaker = None
lastSpeakTime = 0


def readSetting():
    with open('setting.json', "r") as f:
        data = json.loads(f.read())
        return data


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )


def getSenderName(message):
    messageObject = py_.get(message, "author")
    name = py_.get(messageObject, "name")
    id = py_.get(messageObject, "id")
    with open('NameList.json', "r", encoding="utf8") as f:
        data = json.loads(f.read())
        uName = py_.get(data, f"discord.{id}", default=None)
        if uName == None:
            sendToLog(f"New User {id} : {name}")
        else:
            name = uName
    return name


def sendToLog(message):
    # print(message)
    # channel = client.get_channel(LOG_CHANNEL)
    # await channel.send(message)
    pass


def formatMessage(message):
    global lastSpeaker, lastSpeakTime
    name = getSenderName(message)
    id = py_.get(message, "author.id")
    msg = py_.get(message, 'content')
    print(f"Lye Debug formatMessage id : {id}")
    print(f"Lye Debug formatMessage msg : {msg}")
    print(f"Lye Debug formatMessage lastSpeaker1 : {lastSpeaker}")
    if not (lastSpeaker == id and isTimeWithinRange()):
        msg = f"{name}讲, {msg}"
    lastSpeaker = id
    print(f"Lye Debug formatMessage lastSpeaker2 : {lastSpeaker}")
    lastSpeakTime = getCurrentTimeStamp()
    return msg


def getCurrentTimeStamp():
    return int(round(time.time() * 1000))


def isTimeWithinRange():
    global lastSpeakTime
    return (getCurrentTimeStamp() - lastSpeakTime) < readSetting()['timeOverGap']


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    senderName = getSenderName(message)
    str = f"{senderName}讲, {py_.get(message, 'content')}"
    if py_.get(message, 'content')[0] == "/":
        await message.channel.send("Command error")
    else:
        print(str)
        sendToLog(str)
        speakMessage = formatMessage(message)
        speakControl.speak(speakMessage)


client.run(TOKEN)
