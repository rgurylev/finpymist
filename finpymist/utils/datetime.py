import numpy as np
import pandas
from datetime import datetime, timedelta, timezone, date


MIN_DATE = datetime.strptime ('1900-01-01', '%Y-%m-%d')
MAX_DATE = datetime.strptime ('4444-01-01', '%Y-%m-%d')
#TODAY = datetime.strptime (date.today().strftime("%Y-%m-%d"), '%Y-%m-%d').date()
TODAY = date.today()


def to_date(date):
    dt = None
    if type(date) is str:
       dt = datetime.strptime(date[:10], '%Y-%m-%d')if date else ''
    elif type(date) is np.datetime64:
        timestamp = ((date - np.datetime64('1970-01-01T00:00:00'))
                    / np.timedelta64(1, 's'))
        dt = datetime.utcfromtimestamp(timestamp)
    return dt.replace(tzinfo=timezone.utc)

def to_pdate(date):
    dt = None
    if type(date) is str:
       dt = pandas.Timestamp (date)
    elif type(date) is datetime:
       dt = pandas.Timestamp (date)
    return dt




def date_to_string (date):
   return date.strftime ('%d.%m.%Y' ) if date else ''

def date_format (date):
   return date[8:10]+'.'+ date[5:7] + '.' + date[:4] if date else ''

def datetime_format (date):
   return date[8:10]+'.'+ date[5:7] + '.' + date[:4]  + date [11:19]  if date else ''

def now_to_string ():
   return datetime.now().strftime("%d.%m.%Y, %H:%M:%S")