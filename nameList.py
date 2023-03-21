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
        return id in self.read()

    def checkUserValid(self):
        def decorator(handler):
            def wrapper(message):
                if self.checkIsValidUser(message.from_user.id):
                    handler(message)
                else:
                    print(f"User {message.from_user.id} is not valid")
            return wrapper