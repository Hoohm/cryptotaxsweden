import json

class Fees:
    def __init__(self, fees):
        self.fees = fees

    @staticmethod
    def read_from(filename):
        with open(filename, encoding="utf-8-sig") as f:
            d = json.load(f)
            return Fees(d["fees"])
