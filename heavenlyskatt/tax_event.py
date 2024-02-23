import json

class TaxEvent:
    def __init__(self, amount, name:str, income, cost, date):
        self.amount = amount
        self.name = name
        self.income = income
        self.cost = cost
        self.date = date

    @staticmethod
    def headers():
        return ['Amount', 'Name', 'Income', 'Cost']

    def fields(self):
        return [self.amount, self.name, self.income, self.cost]

    def k4_fields(self):
        return [self.amount, self.name, self.income, self.cost,
                self.profit() if self.profit() > 0 else None,
                -self.profit() if self.profit() < 0 else None]

    def profit(self):
        return self.income - self.cost

    @staticmethod
    def read_stock_tax_events_from(filename:str):
        with open(filename, encoding="utf-8-sig") as f:
            d = json.load(f)
            events = []
            for event in d["trades"]:
                events.append(TaxEvent(event["amount"], event["name"], event["income"], event["costbase"]))
            return events
