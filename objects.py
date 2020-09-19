import datetime


class Reminder(object):

    def __init__(self, channel_id, message: str, start_time: datetime.datetime, duration: int):
        """
        Makes a new reminder object.
        :param channel_id: Id of the channel the reminder is to be sent in.
        :param message: The message sent by the bot at the end of the duration
        :param start_time: System time at cooldown start
        :param duration: Number of seconds from start that message is sent.
        """
        self.channel_id = channel_id
        self.message: str = message
        self.start_time: datetime.datetime = start_time
        self.duration: int = duration

    def __eq__(self, other):
        if isinstance(other, Reminder):
            return self.message == other.message and self.duration == other.duration
        return NotImplemented


class Utility:
    pass
