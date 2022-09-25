# -*- coding: utf-8 -*-
import sys
from gtts import gTTS
from playsound import playsound
import os

def speak(sentence, cb=None):
        try:
            tts=gTTS(text=sentence, lang='zh-TW')
            tts.save("temp.mp3")
            playsound("temp.mp3")
            cb()
        except Exception as e:
            print(f"TTS Error : {e}")
            cb()
        finally:
            os.remove("temp.mp3")