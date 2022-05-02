import os
import re
import pytz
import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, shift, fullShift, name_valid, isFeedFormular, isPercentage, reFormatDate

# Configure application
application = Flask(__name__)

# Ensure templates are auto-reloaded
application.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@application.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
application.config["SESSION_FILE_DIR"] = mkdtemp()
application.config["SESSION_PERMANENT"] = False
application.config["SESSION_TYPE"] = "filesystem"
Session(application)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///lambLight.db")

# 'Global variables' class
class DataStore():
    current_patient_id = 0
    first_patient_id = 0
    first_patient_name = ""
    login = 0
    patients = {}
    monitor_hour = 0
    monitor_tracker = 0
    reportSheet_sub = 0

data = DataStore()

# Report Sheet Select Options
rSheet_select_tags = {
    'iv_site': {'None': 1,'R Arm': 1, 'L Arm': 1, 'Both Arm': 1, 'R Wrist': 1, 'L Wrist': 1, 'Both Wrist': 1},
    'picc_site': {'None': 2, 'Left Brachial': 2},
    'tube_feed': {'None': 3, 'PEG': 3, 'DOBHOFF': 3},
    'diet': {'Normal': 4, 'Low Sodium & high Protein': 4, 'Low Carbs': 4, 'No Sodium': 4, 'No Sugar': 4, 'Purée': 4, 'Liquids': 4},
    'neuro_state': {'N/A': 5, 'CONFUSED': 5, 'ORIENTED X3': 5, 'OBTUNDED': 5},
    'pupils': {'PERLA': 6, 'DIALATED': 6, 'Not Reactive To Light': 6},
    'skin': {'INTACT': 7, 'IMPAIRED': 7},
    'wound_care': {'NO': 8, 'YES': 8},
    'heart_sound': {'REGULAR': 9, 'IRREGULAR': 9, 'MUMUR': 9, 'GALLOP': 9},
    'heart_rhythm': {'NSR': 10, 'A-FIB': 10, 'A-FLUTTER': 10, 'TACHYCARDIA': 10, 'BRADYCARDIA': 10},
    'lung_sound': {'CLEAR': 11, 'DIMINISHED': 11, 'COARSE': 11, 'CRACKLES': 11, 'WHEEZES': 11},
    'bowel_sound': {'PRESENT': 12, 'HYPERACTIVE': 12, 'HYPOACTIVE': 12, 'HIGH PITCHED': 12},
    'urinary': {'CONTIENT': 13, 'INCONTIENT': 13, 'FOLEY:URETHRA': 13}
}


@application.route("/", methods=["GET", "POST"])
@login_required
def index():
    """
    Show patient profile, feeding information and medication time
    Allows user to select different patients and view their medical information

    """

    # Get all patient medication hours
    # Used for function mHours which alerts user when patient medication is due
    patient_and_medication = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients) JOIN medication ON id = p_med_id")
    pmed_hours = []

    # Convert from dictionary to 2D array
    for row in patient_and_medication:
        # Store 1D array with patient name and their medication hours
        list1 = []
        for key, value in row.items():
            # Get first name
            if key == "first_name":
                list1.append(value)
            # Get last name
            if key == "last_name":
                list1.append(value)
            # Get medication hours
            if key[0] == "t" and value:
                list1.append(key[1:])
        # 2D array: stores all 1D user arrays
        pmed_hours.append(list1)

    # Get nurse info
    nurse_info = db.execute("SELECT name, shift_start, shift_end, patients FROM nurses WHERE nurse_id=?", session["user_id"])

    # Get current date
    now = datetime.now(pytz.timezone("America/Vancouver"))
    d = now.strftime("%B %d, %Y")
    # Number of submitted forms for patient monitoring
    tracker = data.monitor_tracker

    if not data.login:
        # Get number of residents under nurse and corresponding patients
        p_num = nurse_info[0]['patients']
        # randomly select p_num number of patients
        data.patients = db.execute("SELECT * FROM patients ORDER BY RANDOM() LIMIT ?", p_num)
        patients = data.patients

        # Get first patient's info to display on home page
        data.first_patient_id = data.patients[0]['id']
        data.first_patient_name = data.patients[0]['first_name'] + " " + data.patients[0]['last_name']
        p_name = data.first_patient_name
        data.login = 1
    else:
        # Get name of user selected patient
        p = db.execute("SELECT first_name, last_name FROM patients WHERE id=?", data.current_patient_id)
        p_name = p[0]['first_name'] + " " + p[0]['last_name']

    patients = data.patients

    return render_template("index.html", date=d, tracker=tracker, nurse_info=nurse_info, patients=patients, p_name=p_name, p_m_hrs=pmed_hours)


@application.route("/profile/<name>")
def profile(name):
    """ Displays selected patient's profile with picture, top left of home page """

    # Get selected patient's first and last name
    fn, ln = name.split(" ")
    # Get selected patient's info
    patients = db.execute("SELECT * FROM patients WHERE first_name=? AND last_name=?", fn, ln)
    DP = patients[0]

    # "Broadcasts" current patient's id to other functions
    data.current_patient_id = DP['id']
    # Get dir path of current patient's picture
    pic = DP['picture']

    return render_template("profile.html", DP=DP, pic=pic)


@application.route("/progress/<name>", methods=["GET", "POST"])
def progress(name):
    """ Periodic monitoring on patients """

    # Get local time
    now = datetime.now(pytz.timezone("America/Vancouver"))

    if request.method == "POST":

        # Track form errors
        error = 0
        # Reformat date
        date = now.strftime("%B %d, %Y")
        # Regular expressions
        reg_o_sat = '^([0-1-]?([0-9-]?){2}[%])$'
        reg_bp = '^(([0-9-]?){3}[/][0-9-]?[0-9-]{2})$'
        reg_temp = '^([0-9-][0-9-](\.[0-9][0-9]?)?)$'
        reg_rest = '^(([0-9-]?){3})$'
        # Form fields
        fields = ['bs', 'bp', 'hr', 'temp', 'o_sat', 'rr', 'pain']

        # Error handling
        for field in fields:
            # Ensure form is not empty
            if not request.form.get(field):
                error = 1
                break

            # Ensure field formats are correct
            if field == 'o_sat':
                if not re.search(reg_o_sat, request.form.get(field)):
                    error = 1
                    break
            elif field == 'bp' or field == 'pain':
                if not re.search(reg_bp, request.form.get(field)):
                    error = 1
                    break
            elif field == 'temp':
                if not re.search(reg_temp, request.form.get(field)):
                    error = 1
                    break
            else:
                if not re.search(reg_rest, request.form.get(field)):
                    error = 1
                    break

        # If there is no error increment tracker
        if not error:
            data.monitor_tracker += 1

        # Insert data into db
        db.execute("INSERT INTO patient_monitor (p_monitor_id, monitor_date, time, bs, bp, hr, temp, o_sat, rr, pain) VALUES(?,?,?,?,?,?,?,?,?,?)",
                data.current_patient_id, date, data.monitor_hour, request.form.get("bs"), request.form.get("bp"), request.form.get("hr"), request.form.get("temp"), request.form.get("o_sat"), request.form.get("rr"), request.form.get("pain"))
        return redirect("/")

    else:
        # Get active patient's name
        fn, ln = name.split(" ")
        # Get patient's monitor information
        monitor = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients WHERE first_name=? AND last_name=?) JOIN patient_monitor ON id = p_monitor_id ORDER BY monitor_id DESC LIMIT 1", fn, ln)

        # Desired dictionary element values to be removed
        remove = ["id", "first_name", "last_name", "monitor_id", "p_monitor_id"]
        r2 = ["monitor_date", "time"]

        # Add desired dictionary elements to new array
        mon_temp = {key: value for key,value in monitor[0].items() if key not in remove}

        # Get time and date from dictionary
        mon_time = datetime.strptime(mon_temp["monitor_date"] + " " + str(mon_temp["time"]), "%B %d, %Y %H")
        # Reformat date
        mon_temp['monitor_date'] = mon_time.strftime("%d/%m/%Y")
        # Reformat time add "AM" or "PM" at the end
        mon_temp['time'] = mon_time.strftime("%H %p")

        # Current date
        today_d = now.strftime("%d/%m/%Y")

        # Hour to display on form
        mon_hour = ""
        # Keep track of next hour to be monitored
        if mon_temp['time'] == "07 AM":
            # If "12 PM" and "17 PM" entries are not present
            # Reset to "7 AM"
            if mon_temp['monitor_date'] != today_d:
                data.monitor_hour = 7
                mon_hour = "7 AM"
            else:
                data.monitor_hour = 12
                mon_hour = "12 PM"
        elif mon_temp['time'] == "12 PM":
            # If "17 PM" entry is not present
            # Reset to "7 AM"
            if mon_temp['monitor_date'] != today_d:
                data.monitor_hour = 7
                mon_hour = "7 AM"
            else:
                data.monitor_hour = 17
                mon_hour = "17 PM"
        else:
            data.monitor_hour = 7
            mon_hour = "7 AM"

        return render_template("progress.html", monitor=mon_temp, r2=r2, date=today_d, mon_hour=mon_hour)


@application.route("/patient_medication/<name>")
def patient_medication(name):
    """ Displays selected patient's medication hours, top right of home page """

    # Get selected patient's first and last name
    fn, ln = name.split(" ")
    # Get selected patient's medication info
    meds = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients) JOIN medication ON id = p_med_id WHERE first_name=? AND last_name=?", fn, ln)

    p_med = {}
    i = 0
    for key, value in meds[0].items():
        # Eliminate keys without values and skip first 4 element of dictionary
        if value and i > 3:
            # Remove the letter "t" for time in key (t1(1AM) -> t24(12AM))
            # Remove "," from list of medication
            p_med[int(key[1:])] = value.split(",")
        i += 1

    return render_template("patient_medication.html", p_med=p_med)


@application.route("/patient_feeding/<name>")
def patient_feeding(name):
    """ Displays selected patient's feeding information, bottom right of home page """

    # Get selected patient's first and last name
    fn, ln = name.split(" ")
    # Get selected patient's feeding info
    feed = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients) JOIN feeding ON id = p_feeding_id WHERE first_name=? AND last_name=? ORDER BY feeding_id DESC LIMIT 1", fn, ln)
    DF = feed[0]

    return render_template("patient_feeding.html", DF=DF)


@application.route("/patient_overview")
def patient_overview():
    """ Displays short summery of a patient's previous day observations """

    overV_data = {}
    # Get patient's observation
    if not data.current_patient_id:
        # Randomly selected patient at first home page visit
        overV_data = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients) JOIN patient_overview ON id = p_overview_id WHERE id=? ORDER BY overview_id DESC LIMIT 1", data.first_patient_id)
    else:
        # User selected patient
        overV_data = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients) JOIN patient_overview ON id = p_overview_id WHERE id=? ORDER BY overview_id DESC LIMIT 1", data.current_patient_id)

    DO = overV_data[0]
    DM = db.execute("SELECT * FROM patient_monitor WHERE p_monitor_id=? ORDER BY monitor_id DESC LIMIT 3", DO['id'])

    return render_template("patient_overview.html", DO=DO, DM=DM)


@application.route("/doctors_family")
def doctors_family():
    """ Display name and contact of patient's doctors and emergancy contacts """

    doc_data = {}
    # Get patient's doctor and family information
    if not data.current_patient_id:
        # Randomly selected patient at first home page visit
        doc_data = db.execute("SELECT * FROM ( SELECT id, first_name, last_name, date FROM patients JOIN update_day ON id = p_update_id WHERE id=? ORDER BY update_id DESC LIMIT 1) JOIN doctors_family ON id=p_doctor_id", data.first_patient_id)
    else:
       # User selected patient
        doc_data = db.execute("SELECT * FROM ( SELECT id, first_name, last_name, date FROM patients JOIN update_day ON id = p_update_id WHERE id=? ORDER BY update_id DESC LIMIT 1) JOIN doctors_family ON id=p_doctor_id", data.current_patient_id)

    DFD = doc_data[0]

    return render_template("doctors_family.html", DFD=DFD)


@application.route("/labs")
def labs():
    """ Displays patient's lab information """

    lab_data = {}
    # Get patient's lab information
    if not data.current_patient_id:
        # Randomly selected patient at first home page visit
        lab_data = db.execute("SELECT * FROM ( SELECT id, first_name, last_name, date FROM patients JOIN update_day ON id = p_update_id WHERE id=? ORDER BY update_id DESC LIMIT 1) JOIN labs ON id=p_lab_id", data.first_patient_id)
    else:
        # User selected patient
        lab_data = db.execute("SELECT * FROM ( SELECT id, first_name, last_name, date FROM patients JOIN update_day ON id = p_update_id WHERE id=? ORDER BY update_id DESC LIMIT 1) JOIN labs ON id=p_lab_id", data.current_patient_id)

    # Split lab results
    DL = lab_data[0]
    l = DL['results'].split('. ')
    DL['results'] = l

    # Split medication names
    l = DL['p_meds'].split(',')
    DL['p_meds'] = l

    return render_template("labs.html", DL=DL)


@application.route("/reportSheet", methods=["GET", "POST"])
def reportSheet():
    """
    Retrieve Patient's last overview and feeding database entries
    Prefill the report sheet form with retrieved data
    Insert modifications to overview and feeding database tables

    """
    # Get Patient's overview and feeding information
    patient = {}
    if not data.current_patient_id:
        # Redomly selected patient at first home page visit
        patient = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients) JOIN (SELECT * FROM patient_overview JOIN feeding ON overview_id = feeding_id) ON id = p_overview_id WHERE id=? ORDER BY overview_id DESC LIMIT 1", data.first_patient_id)
    else:
        # User selected patient
        patient = db.execute("SELECT * FROM (SELECT id, first_name, last_name FROM patients) JOIN (SELECT * FROM patient_overview JOIN feeding ON overview_id = feeding_id) ON id = p_overview_id WHERE id=? ORDER BY overview_id DESC LIMIT 1", data.current_patient_id)

    # Get Current date
    now = datetime.now(pytz.timezone("America/Vancouver"))
    d = now.strftime("%B %d, %Y")
    # Form submit tracker
    submitted = data.reportSheet_sub
    # Error message variable
    message = ""

    # Desired dictionary element values from patient overview and feeding tables
    rSheet = ["iv_site", "picc_site", "tube_feed", "diet", "neuro_state", "pupils", "skin", "wound_care",
                "heart_sound", "heart_rhythm", "lung_sound", "bowel_sound", "urinary"]

    patient = patient[0]
    temp_arr = [0] * 13
    if patient:
        # Retrieve desired dictionary element values
        i = 0
        for n in rSheet:
            temp_arr[i] = patient[n].strip()
            i += 1

    # Get patient's name
    name = patient['first_name'] + " " + patient['last_name']

    if request.method == "POST":

        # Validate select tag values
        for r in rSheet:
            if not request.form.get(r) in rSheet_select_tags[r]:
                message = "Invalid " + r.replace("_"," ").upper() + " Selection"
                return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure IV change date is not empty
        if request.form.get("iv_site") != "None" and not request.form.get("iv_change"):
            message = "Missing IV Change Date"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure IV change date is not empty
        if request.form.get("iv_site") == "None" and request.form.get("iv_change"):
            message = "No IV Change Date Required"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure PICC change date is not empty
        if request.form.get("picc_site") != "None" and not request.form.get("picc_change"):
            message = "Missing PICC Change Date"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure PICC change date is not empty
        if request.form.get("picc_site") == "None" and request.form.get("picc_change"):
            message = "No PICC Change Date Required"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure feeding tube rate is not empty
        if not request.form.get("tf_form_rate"):
            message = "Missing Tube Formular & Rate"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure feeding tube rate formular is correct
        if not isFeedFormular(request.form.get("tf_form_rate")):
            message = "Tube Formular & Rate -- incompatible format detected"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure Breakfast is not empty
        if not request.form.get("breakfast"):
            message = "Missing Breakfast"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure breakfast is a percentage
        if not isPercentage(request.form.get("breakfast")):
            message = "Breakfast -- incompatible format detected"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure Lunch is not empty
        if not request.form.get("lunch"):
            message = "Missing Lunch"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure lunch is a percentage
        if not isPercentage(request.form.get("lunch")):
            message = "Lunch -- incompatible format detected"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure Dinner is not empty
        if not request.form.get("dinner"):
            message = "Missing Dinner"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure dinner is a percentage
        if not isPercentage(request.form.get("dinner")):
            message = "Dinner -- incompatible format detected"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure Wound dressing change date is not empty
        if request.form.get("wound_care") != "NO" and not request.form.get("wound_change"):
            message = "Missing Dsg Change Date"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Ensure Secretion Description is not empty
        if not request.form.get("secretion_d"):
            message = "Missing Secretion Description"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Validate Secretion Description text
        if not name_valid(request.form.get("secretion_d")):
            message = "Secretion Description -- incompatible format detected"
            return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)

        # Reformat input date to match db format
        try:
            iv_change_date = reFormatDate("iv_change", request.form.get("iv_change"))
            picc_change_date = reFormatDate("picc_change", request.form.get("picc_change"))
            wound_change_date = reFormatDate("wound_change", request.form.get("wound_change"))
            last_bm_date = reFormatDate("last_bm", request.form.get("last_bm"))
        except:
            return apology("Report Sheet Date Error", 501)

        # Insert data into db
        db.execute("INSERT INTO patient_overview (p_overview_id, overview_date, neuro_state, pupils, skin, wound_care, wound_change, heart_sound, heart_rhythm, lung_sound, bowel_sound , urinary , last_bm , secretion_d ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                patient['id'], d, request.form.get("neuro_state"), request.form.get("pupils"), request.form.get("skin"), request.form.get("wound_care"), wound_change_date, request.form.get("heart_sound"), request.form.get("heart_rhythm"), request.form.get("lung_sound"), request.form.get("bowel_sound"), request.form.get("urinary"), last_bm_date, request.form.get("secretion_d"))

        db.execute("INSERT INTO feeding (p_feeding_id, date, iv_site, iv_change, picc_site, picc_change, tube_feed, tf_form_rate, diet, breakfast, lunch, dinner) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                patient['id'], d, request.form.get("iv_site"), iv_change_date, request.form.get("picc_site"), picc_change_date, request.form.get("tube_feed"), request.form.get("tf_form_rate"), request.form.get("diet"), request.form.get("breakfast"), request.form.get("lunch"), request.form.get("dinner"))

        # Redirect to home page
        data.reportSheet_sub = 1
        return redirect("/")
    else:
        data.reportSheet_sub = 0
        return render_template("reportSheet.html", submitted=submitted, patient=patient, name=name, date=d, feed=temp_arr, message=message)



@application.route("/login", methods=["GET", "POST"])
def login():
    """ Form validation and user log in """

    # Error message variable
    message = ""
    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure form is not empty
        if not request.form.get("username") and not request.form.get("password") and not request.form.get("shift_start") and not request.form.get("shift_end") and not request.form.get("patients"):
            message = "Missing Fields"
            return render_template("login.html", message=message)

        # Ensure Start of Shift was submitted
        if not request.form.get("shift_start"):
            message = "Missing Start of Shift"
            return render_template("login.html", message=message)

        # Check start of shift format
        if not shift(request.form.get("shift_start")):
            message = "Start of Shift -- incompatible format detected"
            return render_template("login.html", message=message)

        # Ensure End of Shift was submitted
        if not request.form.get("shift_end"):
            message = "Missing End of Shift"
            return render_template("login.html", message=message)

        # Check end of shift format
        if not shift(request.form.get("shift_end")):
            message = "End of Shift -- incompatible format detected"
            return render_template("login.html", message=message)

        # Ensure shift is 8 hours
        if not fullShift(request.form.get("shift_start"), request.form.get("shift_end")):
            message = "Duration of shift must be 8 hours"
            return render_template("login.html", message=message)

        # Ensure number of patients was submitted
        if not request.form.get("patients"):
            message = "Missing Number of Patients"
            return render_template("login.html", message=message)

        # Ensure number of patients format is correct
        if not request.form.get("patients").isnumeric():
            message = "Number of Patients -- incompatible format detected"
            return render_template("login.html", message=message)

        if int(float(request.form.get("patients"))) > 6:
            message = "Patients must be between 2-6"
            return render_template("login.html", message=message)

        # Ensure Username was submitted
        if not request.form.get("username"):
            message = "Missing Username and/or Password"
            return render_template("login.html", message=message)

        if not name_valid(request.form.get("username")):
            message = "Username -- incompatible format detected"
            return render_template("register.html", message=message)

        # Ensure Password was submitted
        if not request.form.get("password"):
            message = "Missing Username and/or Password"
            return render_template("login.html", message=message)

        if len(request.form.get("password")) < 8:
            message = "Password Too Short"
            return render_template("register.html", message=message)

        # Get username and password from database
        rows = db.execute("SELECT * FROM nurses WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["p_hash"], request.form.get("password")):
            message = "Invalid Username and/or Password"
            return render_template("login.html", message=message)

        # Remember which user has logged in
        session["user_id"] = rows[0]["nurse_id"]
        db.execute("UPDATE nurses SET shift_start=? , shift_end=? , patients=? WHERE username=?", request.form.get(
            "shift_start").upper(), request.form.get("shift_end").upper(), int(request.form.get("patients")), request.form.get("username"))

        # Redirect user to home page
        data.login = 0
        return redirect("/")

    else:
        return render_template("login.html", message=message)


@application.route("/register", methods=["GET", "POST"])
def register():
    """ Form validation and user registration """

    # Error message variable
    message = ""

    if request.method == "POST":
        # Ensure form is not empty
        if not request.form.get("username") and not request.form.get("password") and not request.form.get("f_name") and not request.form.get("l_name"):
            message = "Missing Fields"
            return render_template("register.html", message=message)

        # Ensure First Name was submitted
        if not request.form.get("f_name"):
            message = "Missing First Name "
            return render_template("register.html", message=message)

        if not name_valid(request.form.get("f_name")):
            message = "First Name -- incompatible format detected"
            return render_template("register.html", message=message)

        # Ensure Last Name was submitted
        if not request.form.get("l_name"):
            message = "Missing Last Name"
            return render_template("register.html", message=message)

        if not name_valid(request.form.get("l_name")):
            message = "Last Name -- incompatible format detected"
            return render_template("register.html", message=message)

        # Ensure Username was submitted
        if not request.form.get("username"):
            message = "Missing Username"
            return render_template("register.html", message=message)

        if not name_valid(request.form.get("username")):
            message = "Username -- incompatible format detected"
            return render_template("register.html", message=message)

        # Ensure Username does not already exist
        rows = db.execute("SELECT count(*) AS count FROM nurses WHERE username=?", request.form.get("username"))
        if rows[0]["count"]:
            message = "Username Already Exists"
            return render_template("register.html", message=message)

        # Ensure Password was submitted
        if not request.form.get("password"):
            message = "Missing Password"
            return render_template("register.html", message=message)

        if len(request.form.get("password")) < 8:
            message = "Password Too Short"
            return render_template("register.html", message=message)

        # Ensure Passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            message = "Passwords do not Match"
            return render_template("register.html", message=message)

        # Concatinate lastname and firstname and create user
        name = request.form.get("f_name").strip() + " " + request.form.get("l_name").strip()
        db.execute("INSERT INTO nurses (name , username, p_hash , shift_start , shift_end , patients) VALUES(?, ?, ?, ?, ?, ?)", name, request.form.get(
            "username"), generate_password_hash(request.form.get("password")), 'None', 'None', 'None')

        # Redirect user to login page
        message = ""
        return render_template("login.html", message=message)
    else:
        return render_template("register.html", message=message)


@application.route("/logout")
def logout():
    """Log nurse out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    application.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    application.run()


