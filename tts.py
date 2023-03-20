# -*- coding: utf-8 -*-

def speak(sentence, cb=None):
    import sys
    import os
    from gtts import gTTS
    from playsound import playsound

    try:
        with open("temp.mp3", "wb") as f:
            tts = gTTS(text=sentence, lang='zh-TW')
            tts.write_to_fp(f)
        playsound("temp.mp3")
    except Exception as e:
        print(f"TTS Error : {e}")
    finally:
        os.remove("temp.mp3")
        if cb is not None:
            cb()
