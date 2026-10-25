ATTENDEASE — STUDENT ATTENDANCE ANALYTICS
==========================================

WHAT IS INCLUDED
- app.py: the Streamlit website.
- attendance_data.csv: 20 fictional student records.
- requirements.txt: Python packages needed to run the website.
- README.txt: these instructions.

IMPORTANT
This project is designed to run on your own Windows computer. The files have been generated here, but this environment has not launched a Streamlit web server, so do not treat the app as runtime-tested.

1. INSTALL PYTHON
- Open the official Python downloads page: https://www.python.org/downloads/windows/
- Download a current stable Python 3 release.
- Run the installer.
- IMPORTANT: tick the checkbox named "Add python.exe to PATH" if it appears.
- Choose Install Now and wait until installation finishes.

2. DOWNLOAD AND EXTRACT THE PROJECT
- Download the AttendEase_Project.zip file.
- In File Explorer, right-click it and choose Extract All.
- Open the extracted AttendEase folder. You should see app.py, attendance_data.csv, requirements.txt and README.txt.

3. OPEN COMMAND PROMPT IN THE PROJECT FOLDER
- Open the AttendEase folder in File Explorer.
- Click the address bar at the top of the folder window.
- Type cmd and press Enter.
- A black Command Prompt window should open in that folder.

4. CHECK PYTHON
Type this command and press Enter:
    py --version
You should see a Python version. If Windows says the command is not recognized, try:
    python --version
If neither works, reinstall Python and make sure it was added to PATH.

5. INSTALL THE LIBRARIES
In the same Command Prompt window, copy and paste:
    py -m pip install -r requirements.txt
Then press Enter and wait for it to finish.
If the py command did not work but python did, use:
    python -m pip install -r requirements.txt

6. START THE WEBSITE
In that same Command Prompt window, type:
    py -m streamlit run app.py
Then press Enter.
If you use python instead of py, run:
    python -m streamlit run app.py

7. OPEN THE WEBSITE
Streamlit normally opens your default browser automatically. If it does not, look in the Command Prompt for an address like:
    http://localhost:8501
Copy that address into Chrome, Edge, or another browser.
Keep the Command Prompt window open while you use the website. To stop the server, click the Command Prompt window and press Ctrl+C.

8. TEST THE MAIN FEATURES
- Dashboard: check the summary cards and low-attendance list.
- Student Records: search for a student; try adding a new student; edit a record; test deletion only with a record you are happy to remove.
- Attendance Calculator: try Total Days 100 and Present Days 80. Expected: 20 absent days and 80% attendance.
- Data Analysis: compare the calculated average, highest, lowest, and category counts.
- Visualizations: check the bar chart and pie chart.
- CSV Upload: download the sample CSV, then upload it. Click "Use uploaded dataset" to replace the active data.
- Reports: filter below 75% and download the report CSV.
- About Project: read the abstract, methodology, formula, limitations, and future enhancements.
- Restore sample data: use the button near the bottom of About Project to return to the original sample dataset.

9. HOW DATA IS SAVED
- Changes are stored in Streamlit session state while the active browser session is running.
- The app also tries to save a local backup called attendance_saved.csv in the same folder as app.py.
- When the app starts again, it loads attendance_saved.csv if it exists; otherwise it loads attendance_data.csv.
- Keep the project folder writable. If local saving fails, the app will show a warning.
- This is a single-computer academic demo, not a secure database or multi-user system.

10. SHORT REVIEW 3 EXPLANATION
"My project is AttendEase — Student Attendance Analytics. It helps analyze student attendance records from a CSV file. Python is the main programming language. Pandas reads and validates the CSV, calculates absent days and attendance percentages, filters records, and calculates summary statistics. Matplotlib creates the bar chart and pie chart. Streamlit provides the website pages, forms, dashboard, CSV upload, and download features. The attendance formula is Present Days divided by Total Working Days multiplied by 100. The sample dataset contains fictional students. A limitation is that the local CSV backup is intended for a single computer; a database could be added in the future."

TROUBLESHOOTING
- If a command fails, check that Command Prompt is open inside the folder containing app.py.
- If packages fail to install, check your internet connection and try the installation command again.
- If port 8501 is already being used, Streamlit may show another local address; use the address it prints.
- Do not close Command Prompt while using the website.
