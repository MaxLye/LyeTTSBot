import json
import pydash as py_


class Settings:
    def __init__(self, fileName) -> None:
        self.fileName = fileName

    def read(self, key=None):
        with open(self.fileName, "r") as f:
            data = json.load(f)
            return py_.get(data, key)

    def setSendMessageCallback(self, callback):
        self.sendMessageCB = callback

    def write(self, key, value):
        with open(self.fileName, "r+") as f:
            data = json.load(f)
            print("Write setting {} with {}".format(key, value))
            data[key] = value
            f.seek(0)
            json.dump(data, f)
            f.truncate()

    def checkAdmin(self):
        def decorator(handler):
            def wrapper(message):
                if message.from_user.id in self.read("admins"):
                    handler(message)
                else:
                    self.sendMessageCB(message.chat.id, "You are not admin")
        return decorator

    def isAdmin(self, userID):
        return userID in self.read("admins")
