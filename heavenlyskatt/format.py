from enum import Enum

class Format(Enum):
    pdf = 'pdf'
    sru = 'sru'
    def __str__(self):
        return self.value
