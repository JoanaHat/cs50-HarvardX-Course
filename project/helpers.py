import re
from datetime import datetime
from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def shift(time):
    """ Checks the format of time inputed """

    # Format 1am/1Am/1AM/1aM, 1pm/1Pm... etc.
    regex ='(^0?[1-9][aApP][mM]$)|(^1[0-2][aApP][mM]$)'
    if re.search(regex,time):
        return 1
    else:
        return 0


def fullShift(shift1, shift2):
    """ Checks start to end shift is 8 hours """

    # Convert shift hours to 24 hour format
    start = shift_hour(shift1)
    finish = shift_hour(shift2)

    # Calculate total shift hours
    hours = finish - start

    # Handle finish hours smaller than start hours
    if finish < start:
        hours /= 2

    # Ensure shift is 8 hours
    if abs(hours) == 8:
        return 1
    else:
        return 0


def shift_hour(t):
    """ Convert to 24 hour format """

    time = 0
    if len(t) == 3:
        # Convert from 12 hour format to 24
        if t[1] == 'p' or t[1] == 'P':
            time = (int(t[0]) + 12)
        else:
            time = int(t[0])
    else:
        if t[2] == 'p' or t[2] == 'P':
            time = (int(t[:2]) + 12)
        else:
            time = int(t[:2])

    return time


def name_valid(name):
    """ Checks for correct name format """

    # Only letters, numbers and a few symbols
    regex ="^([- \w\d\u00c0-\u024f\.\'\!\&\,\-\/]+)$"
    if re.search(regex,name):
        return 1
    else:
        return 0


def isFeedFormular(rate):
    """ Checks for correct feeding rate formular """

    # Only letters, numbers and a few symbols
    regex ='^([- \w\d\u00c0-\u024f\/\.\(\)\&\=\,]+)$'
    if re.search(regex,rate):
        return 1
    else:
        return 0


def isPercentage(num):
    """ Checks if input is a percentage """

    # Only numbers followed by '%' symbol
    regex ='^([0-9-]+[%])$'
    if re.search(regex,num):
        return 1
    else:
        return 0


def reFormatDate(dateName, dateStr):
    """ Reformat calendar date to database date format """

    # If there is no input
    if dateStr == "":
        db_date = "N/A"
        return db_date
    # If time is required
    elif dateName == "last_bm":
        reFormat_date = datetime.strptime(dateStr,"%Y-%m-%d %H:%M")
        db_date = reFormat_date.strftime("%B %d, %Y %I:%M %p")
        return db_date
    # If no time is required
    else:
        reFormat_date = datetime.strptime(dateStr,"%Y-%m-%d")
        db_date = reFormat_date.strftime("%B %d, %Y")
        return db_date