import json

class PersonalDetails:
    def __init__(self, json_path):
        filename = json_path

        with open(filename, encoding="utf-8-sig") as f:
            d = json.load(f)
            self.namn = d["namn"]
            self.personnummer = d["personnummer"]
            self.postnummer = d["postnummer"]
            self.postort = d["postort"]
