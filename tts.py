# -*- coding: utf-8 -*-
import sys
from gtts import gTTS
from pygame import mixer
import tempfile

def speak(sentence, cb=None):
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        try:
            tts=gTTS(text=sentence, lang='zh-TW')
            tts.save('{}.mp3'.format(fp.name))
            mixer.init()
            mixer.music.load('{}.mp3'.format(fp.name))
            mixer.music.play(1)
            while mixer.music.get_busy():
                pass
            if cb != None:
                cb()
        except Exception as e:
            print(f"TTS Error : {e}")
            cb()
