import datetime
from dateutil import tz


# 09-87
def get_date(unformatted_date):
    if "+" in unformatted_date:
        date = datetime.datetime.today() + datetime.timedelta(days=int(unformatted_date[1:]))
        formatted_date = str(date.month).zfill(2) + "-" + str(date.day).zfill(2)
        return valid_date(formatted_date)
    elif "!" in unformatted_date:
        date = unformatted_date[1:]
        month = datetime.date.today().month
        formatted_date = str(month).zfill(2) + "-" + date.zfill(2)
        return valid_date(formatted_date)
    else:
        # user gave good value - contains both month and day
        return valid_date(unformatted_date)


# check if user give invalid date value such as 01-35
def valid_date(formatted_date):
    if formatted_date.lower() == "today":
        return (datetime.date.today()).strftime("%m-%d")
    if formatted_date.lower() == "tomorrow":
        return (datetime.date.today() + datetime.timedelta(days=1)).strftime("%m-%d")
    try:
        datetime.datetime.strptime(formatted_date, "%m-%d")
        return formatted_date
    except:  # except ValueError but in case other Error was triggered and not able to function
        print("Unsupported")
        return None


# set sacanning process at 9AM.
def get_scheduled_time():
    return datetime.time(9, 00, tzinfo = tz.gettz('Asia/Jerusalem'))

    def daynum_to_string(daynum):
        if daynum == 0:
            return "Today"
        elif daynum == 1:
            return "Tomorrow"
        else:
            return f"{daynum} Days from now"
