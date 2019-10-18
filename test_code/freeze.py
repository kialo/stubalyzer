from datetime import datetime

from freezegun import freeze_time


def func() -> datetime:
    return datetime.utcnow()


wrapped = freeze_time(datetime.utcfromtimestamp(1000))(func)

print(func())
print(wrapped())
