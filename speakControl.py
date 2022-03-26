import tts
speakArr = []
speaking = False

def speak(speakMessage = None):
    if(speakMessage != None):
        speakArr.append(speakMessage)
    global speaking
    if len(speakArr) and not speaking:
        speaking = True
        msg = speakArr.pop(0)
        tts.speak(msg, speakEnd)


def speakEnd():
    global speaking
    speaking = False
    speak()