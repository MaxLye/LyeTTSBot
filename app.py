from telegram3 import Telegram
from NameList import NameList
from settings import Settings
from speakControl import SpeakControl

setting = Settings('setting.json')
nameLists = NameList()
nameLists.setSetting(setting)
speakControl = SpeakControl(setting=setting, nameList=nameLists)


telegram = Telegram(speakCallback=speakControl.speak,
                    setting=setting, nameList=nameLists)
