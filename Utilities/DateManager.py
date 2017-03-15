import datetime


class Manager:

    @staticmethod
    def datetime_handler(x):
        if x is None:
            return None
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError("Unknown type")
