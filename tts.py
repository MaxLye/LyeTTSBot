# -*- coding: utf-8 -*-
import sys
from gtts import gTTS
#from pygame import mixer
from playsound import playsound

def speak(sentence, cb=None):
        try:
            tts=gTTS(text=sentence, lang='zh-TW')
            tts.save('./temp.mp3')
            #mixer.init()
            #mixer.music.load('{}.mp3'.format(fp.name))
            #mixer.music.play(1)
            #while mixer.music.get_busy():
            #    pass
            #if cb != None:
            #    cb()
            playsound('./temp.mp3')
            cb()
        except Exception as e:
            print(f"TTS Error : {e}")
            cb()
