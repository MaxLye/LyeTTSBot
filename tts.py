# -*- coding: utf-8 -*-
import sys
from gtts import gTTS
from pygame import mixer
import tempfile
def speak(sentence, lang = 'zh'):
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts=gTTS(text=sentence, lang=lang)
        tts.save('{}.mp3'.format(fp.name))
        mixer.init()
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play(1)
        while mixer.music.get_busy():
            pass