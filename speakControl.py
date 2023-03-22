from NameList import NameList
from settings import Settings
import tts
from queue import Queue
import pydash as py_
import time


class SpeakControl:
    def __init__(self, setting: Settings, nameList: NameList) -> None:
        self.setting = setting
        self.nameList = nameList
        self.speakQueue = Queue()
        self.lastSpeaker = None
        self.lastSpeakTime = 0

    def speak(self, message=None):
        if not message:
            return

        timeNow = int(round(time.time() * 1000))
        speakName = self.setting.read(
            "timeOverGap") < timeNow - self.lastSpeakTime
        speakerName = py_.get(self.nameList.read(), str(py_.get(message, "from_user.id")), "沒有名字")
        self.lastSpeakTime = timeNow
        userID = py_.get(message, "from_user.id")
        if self.lastSpeaker != userID:
            self.lastSpeaker = userID
            tts.speak(f"{speakerName}讲, {py_.get(message, 'text')}")
        else:
            if speakName:
                name = f"{speakerName}讲, " if speakName else None
                tts.speak(f"{name}{py_.get(message, 'text')}")
            else:
                tts.speak(py_.get(message, "text"))
