import datetime


class ReminderData:
    def __init__(self, row) -> None:
        self.reminder_id = row[0]
        self.chat_id = row[1]
        self.message = row[2]
        self.time = row[3]
        self.fired = row[4]
    

    def __repr__(self) -> str:
        return f"Message: {self.message}; At time: {self.time}"

    def should_be_fired(self):
        return self.fired is False and datetime.datetime.today() >= self.time
    