import json


class NameList:
    def read(self):
        with open('NameList.json', "r") as f:
            return json.load(f)

    def write(self, id, name=None):
        data = NameList.readNameList()
        data[id] = name if name is not None else None
        with open('NameList.json', 'w') as f:
            json.dump(data, f)

    def setSendMessageCallback(self, callback):
        self.sendMessageCB = callback

    def checkIsValidUser(self, id):
        return self.read().get(str(id)) != None

    def setSetting(self, setting):
        self.setting = setting

    def checkUserValid(self):
        def decorator(handler):
            def wrapper(message):
                if self.checkIsValidUser(message.chat.id):
                    handler(message)
                else:
                    self.sendMessageCB(
                        message.chat.id, "You are not in the name list, please contact admin to add you in the list")
            return wrapper
        return decorator
