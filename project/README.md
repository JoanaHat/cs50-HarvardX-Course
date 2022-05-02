# About The Project
## Project Name: LambLight Report Sheet
## **[Video Link](https://youtu.be/WA6FCQt2Brg)**


Nurses need a brief summary of the overall health of all patients under them during a shift.
Many nurses choose to be casual nurses in more than one place, meeting 1 or more new patients on every shift.
Reading patient summaries in a short timeframe becomes a tedious task.
In a fast-paced and somewhat chaotic environment, a tool is needed to scan patient information in a timely manner.
Lamplight Report Sheet attempts to mitigate this problem by providing quick and summarized information for each patient.
Additionally, at the end of each shift, nurses need to chart all their observations and procedures done to all patients during a shift, this too can be very time-consuming.
The end of shift report on the app is almost completely prefilled to save time at the end of a shift.

---

## Built With
- Flask
- cs50 library
- SQLite


## Prerequisites
- requirements.txt file (included)
- lambLight.db database (included)
- cs50 IDE

---

## Install and Run Project

### cs50 IDE
1. If you don’t already have one, create a GitHub account here.
2. Visit ide.cs50.io.
3. Click Sign in with GitHub then login into your GitHub account and authorize the CS50 IDE GitHub app if prompted.
4. Once you log in, you will automatically be forwarded to CS50 IDE! Hereafter, you may simply return to ide.cs50.io to log in and return to CS50 IDE, where all your files and settings are preserved.
[For more information] (https://cs50.readthedocs.io/ide/online/)
5. Clone this repo

### Access local host link to application
'''python
    ~/ $ cd project/
    ~/project/ $ flask run
    * Serving Flask app "application.py" (lazy loading)
    * Environment: development
    * Debug mode: off
    * Running on https://ide-76bfed53dbee4b1bb3806d24798f5801-8080.cs50.ws/ (Press CTRL+C to quit)
    * Restarting with stat
'''
Click on the link and select open

### Create an account and explore app
Register yourself ("As a nurse")
Log in to your account:
    - Enter start of shift and end of shift (must be 8 hours shift)
    - Enter number of patients under you; min=1, max=6
    - Enter username and password
    - Explore App

---

## Usage

To Display patient monitor form (if not actively dispalying)
- In index.html
- Inside script section
- Modify "hr" to your current hour (eg. if it is 4:30pm, hr will equal 16)
'''python
    // Selected hours for monitoring patients
    if (hr == 7 || hr == 12 || hr == 18) {
'''

To Display medication alert message (if not actively dispalying)
- In index.html
- Inside script section
- Modify "hour" to your current hour (eg. if it is 4:30pm, hr will equal 16)
'''python
    // If time is 12 AM getHours returs 0
    if (!g_hour) {
            g_hour = 24;
    }
    hour = g_hour;
'''

---

## Contact
Joanita - criativajojo@gmail.com

---

## Acknowledgments
Harvard cs50
Bootstrap Forms
w3school - SQL, CSS, HTML and JS
Font Awesome
Favicons
