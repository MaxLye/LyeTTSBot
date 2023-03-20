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