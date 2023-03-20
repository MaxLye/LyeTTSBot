import json


class Settings:
    def read(self, key):
        with open('setting.json', "r") as f:
            data = json.load(f)
            return data[key]

    def write(self, key, value):
        with open('setting.json', "r+") as f:
            data = json.load(f)
            print("Write setting {} with {}".format(key, value))
            data[key] = value
            f.seek(0)
            json.dump(data, f)
            f.truncate()
