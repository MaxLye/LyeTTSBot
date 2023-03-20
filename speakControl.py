import tts
from queue import Queue

speakQueue = Queue()


def speak(speakMessage=None):
    if speakMessage:
        speakQueue.put(speakMessage)
    if not speakQueue.empty():
        msg = speakQueue.get()
        tts.speak(msg, speakEnd)


def speakEnd():
    speak()
