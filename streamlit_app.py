import io
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = APP_DIR / "attendance_data.csv"
LOCAL_FILE = APP_DIR / "attendance_saved.csv"

REQUIRED_COLUMNS = ["Student_ID", "Student_Name", "Department", "Total_Days", "Present_Days"]
DISPLAY_NAMES = {
    "Student_ID": "Student ID",
    "Student_Name": "Student Name",
    "Department": "Department",
    "Total_Days": "Total Working Days",
    "Present_Days": "Present Days",
    "Absent_Days": "Absent Days",
    "Attendance_Percentage": "Attendance %",
}

st.set_page_config(page_title="AttendEase | Attendance Analytics", page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fc;
    color: #1e293b;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102a56 0%, #173f75 100%);
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Sidebar navigation and labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #ffffff !important;
}

/* ===== MAIN HEADINGS ===== */
h1, h2, h3 {
    color: #16345c !important;
    font-weight: 700 !important;
}

p, label, .stMarkdown {
    color: #334155;
}

/* ===== HERO BANNER ===== */
.hero {
    padding: 1.6rem 1.8rem;
    border-radius: 18px;
    background: linear-gradient(110deg, #123c78, #2878c8);
    color: #ffffff !important;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 18px rgba(18, 60, 120, 0.15);
}

.hero h1 {
    color: #ffffff !important;
    margin: 0;
    font-size: 2rem;
}

.hero p {
    color: #eaf3ff !important;
    margin-top: 0.5rem;
}

/* ===== DASHBOARD METRIC CARDS ===== */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.05);
}

/* Metric labels */
div[data-testid="stMetricLabel"] p {
    color: #64748b !important;
    font-size: 0.92rem !important;
}

/* Metric numbers */
div[data-testid="stMetricValue"] {
    color: #123c78 !important;
    font-weight: 750 !important;
}

/* ===== DATA TABLES ===== */
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    background: #ffffff;
    border-radius: 12px;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: #1d5fa7;
    color: #ffffff !important;
    border: none;
    border-radius: 9px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #123c78;
    color: #ffffff !important;
    border: 1px solid #123c78;
}

/* ===== INPUT FIELDS ===== */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff;
    color: #1e293b !important;
    border-radius: 8px;
}

/* ===== SECTION SPACING ===== */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ===== SMALL HELPER TEXT ===== */
.metric-note {
    color: #52647a !important;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)


def load_and_validate_csv(uploaded_file):
    """Read and validate a CSV, returning a cleaned dataframe or raising ValueError."""
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        raise ValueError(f"Could not read the CSV file: {exc}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))

    df = df[REQUIRED_COLUMNS].copy()
    df["Student_ID"] = pd.to_numeric(df["Student_ID"], errors="coerce")
    df["Total_Days"] = pd.to_numeric(df["Total_Days"], errors="coerce")
    df["Present_Days"] = pd.to_numeric(df["Present_Days"], errors="coerce")

    if df[["Student_ID", "Total_Days", "Present_Days"]].isna().any().any():
        raise ValueError("Student_ID, Total_Days, and Present_Days must contain valid numbers.")
    for col in ["Student_ID", "Total_Days", "Present_Days"]:
        if ((df[col] % 1) != 0).any():
            raise ValueError(f"{col} must contain whole numbers.")
        df[col] = df[col].astype(int)

    if df["Student_ID"].duplicated().any():
        duplicates = df.loc[df["Student_ID"].duplicated(keep=False), "Student_ID"].astype(str).unique()
        raise ValueError("Duplicate Student_ID value(s): " + ", ".join(duplicates))
    if (df["Student_ID"] <= 0).any():
        raise ValueError("Student_ID values must be greater than zero.")
    if df["Student_Name"].isna().any() or df["Student_Name"].astype(str).str.strip().eq("").any():
        raise ValueError("Every student must have a name.")
    if df["Department"].isna().any() or df["Department"].astype(str).str.strip().eq("").any():
        raise ValueError("Every student must have a department.")
    if (df["Total_Days"] < 0).any() or (df["Present_Days"] < 0).any():
        raise ValueError("Working days and present days cannot be negative.")
    if (df["Present_Days"] > df["Total_Days"]).any():
        raise ValueError("Present Days cannot be greater than Total Days.")
    df["Student_Name"] = df["Student_Name"].astype(str).str.strip()
    df["Department"] = df["Department"].astype(str).str.strip()
    return add_calculated_columns(df)


def add_calculated_columns(df):
    df = df.copy()
    df["Absent_Days"] = df["Total_Days"] - df["Present_Days"]
    df["Attendance_Percentage"] = (
        df["Present_Days"].div(df["Total_Days"].where(df["Total_Days"] != 0)).mul(100).fillna(0).round(2)
    )
    return df


def category_for(value):
    if value >= 90:
        return "Excellent"
    if value >= 75:
        return "Good"
    if value >= 60:
        return "Low"
    return "Critical"


def add_categories(df):
    df = df.copy()
    df["Category"] = df["Attendance_Percentage"].apply(category_for)
    return df


def format_table(df):
    shown = df.copy()
    shown = shown.rename(columns=DISPLAY_NAMES)
    if "Attendance %" in shown:
        shown["Attendance %"] = shown["Attendance %"].map(lambda x: f"{x:.2f}%")
    return shown


def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


def persist_current_data(df):
    """Save raw columns locally. This works only when the folder is writable."""
    try:
        df[REQUIRED_COLUMNS].to_csv(LOCAL_FILE, index=False)
        return True, None
    except Exception as exc:
        return False, str(exc)


def initialize_data():
    if "attendance_df" not in st.session_state:
        source = LOCAL_FILE if LOCAL_FILE.exists() else SAMPLE_FILE
        try:
            st.session_state.attendance_df = load_and_validate_csv(source)
        except Exception:
            st.session_state.attendance_df = load_and_validate_csv(SAMPLE_FILE)


def save_changes(df, message="Changes saved."):
    st.session_state.attendance_df = add_calculated_columns(df[REQUIRED_COLUMNS])
    ok, error = persist_current_data(st.session_state.attendance_df)
    if ok:
        st.success(message + " A local backup was also saved.")
    else:
        st.warning(message + f" Session data is updated, but the local backup could not be saved: {error}")


initialize_data()

with st.sidebar:
    st.markdown("## 📊 AttendEase")
    st.caption("Student Attendance Analytics")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Student Records", "Attendance Calculator", "Data Analysis",
         "Visualizations", "CSV Upload", "Reports",],
    )
    st.divider()
    st.caption("B.Tech Information Technology")
    st.caption("Aditya University")
    st.caption("Data Analysis Essentials • Review 3")

df = add_categories(st.session_state.attendance_df)
total_students = len(df)
average_attendance = df["Attendance_Percentage"].mean() if total_students else 0
below_75 = int((df["Attendance_Percentage"] < 75).sum())
total_working_days = int(df["Total_Days"].max()) if total_students else 0

st.markdown("""
<div class="hero">
  <h1>AttendEase</h1>
  <p>Student Attendance Analytics · Understand attendance data with Python, Pandas and Matplotlib.</p>
</div>
""", unsafe_allow_html=True)


if page == "Dashboard":
    st.subheader("Dashboard Overview")
    st.write("A live summary of the attendance dataset currently loaded in the application.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", f"{total_students}")
    c2.metric("Average Attendance", f"{average_attendance:.2f}%")
    c3.metric("Below 75%", f"{below_75}")
    c4.metric("Working Days", f"{total_working_days}")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### Attendance distribution")
        if total_students:
            counts = df["Category"].value_counts().reindex(["Excellent", "Good", "Low", "Critical"], fill_value=0)
            fig, ax = plt.subplots(figsize=(7, 4))
            counts.plot(kind="bar", ax=ax)
            ax.set_title("Students by Attendance Category")
            ax.set_xlabel("Attendance category")
            ax.set_ylabel("Number of students")
            ax.tick_params(axis="x", rotation=0)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No student records are available.")
    with right:
        st.markdown("### Students needing attention")
        low = df[df["Attendance_Percentage"] < 75].sort_values("Attendance_Percentage")
        if low.empty:
            st.success("No students are currently below 75%.")
        else:
            st.dataframe(format_table(low[["Student_ID", "Student_Name", "Department", "Attendance_Percentage"]]), use_container_width=True, hide_index=True)
    st.caption("Categories: Excellent ≥ 90%; Good 75–89.99%; Low 60–74.99%; Critical < 60%. Zero working days are treated as 0%.")


elif page == "Student Records":
    st.subheader("Student Records")
    st.write("Search, filter, add, edit, or delete records. Student IDs must be unique.")
    search_text = st.text_input("Search by student ID, name, or department")
    departments = ["All"] + sorted(df["Department"].dropna().unique().tolist())
    chosen_department = st.selectbox("Filter by department", departments)
    filtered = df.copy()
    if search_text.strip():
        term = search_text.strip().lower()
        filtered = filtered[
            filtered["Student_ID"].astype(str).str.contains(term, case=False)
            | filtered["Student_Name"].str.lower().str.contains(term, na=False)
            | filtered["Department"].str.lower().str.contains(term, na=False)
        ]
    if chosen_department != "All":
        filtered = filtered[filtered["Department"] == chosen_department]
    st.dataframe(format_table(filtered[["Student_ID", "Student_Name", "Department", "Total_Days", "Present_Days", "Absent_Days", "Attendance_Percentage"]]), use_container_width=True, hide_index=True)

    with st.expander("➕ Add a student"):
        with st.form("add_student_form", clear_on_submit=True):
            a, b = st.columns(2)
            new_id = a.number_input("Student ID", min_value=1, step=1, value=121)
            new_name = b.text_input("Student name")
            new_dept = a.text_input("Department", value="IT")
            new_total = b.number_input("Total working days", min_value=0, step=1, value=100)
            new_present = a.number_input("Present days", min_value=0, step=1, value=80)
            add_submit = st.form_submit_button("Add student")
        if add_submit:
            current = st.session_state.attendance_df
            if int(new_id) in current["Student_ID"].tolist():
                st.error("That Student ID already exists. Please use a unique ID.")
            elif not new_name.strip() or not new_dept.strip():
                st.error("Student name and department cannot be blank.")
            elif new_present > new_total:
                st.error("Present days cannot be greater than total working days.")
            else:
                record = pd.DataFrame([{
                    "Student_ID": int(new_id), "Student_Name": new_name.strip(),
                    "Department": new_dept.strip(), "Total_Days": int(new_total),
                    "Present_Days": int(new_present)
                }])
                save_changes(pd.concat([current[REQUIRED_COLUMNS], record], ignore_index=True), "Student added.")
                st.rerun()

    with st.expander("✏️ Edit a student"):
        current = st.session_state.attendance_df
        if current.empty:
            st.info("There are no records to edit.")
        else:
            selected_id = st.selectbox("Choose Student ID to edit", current["Student_ID"].tolist(), key="edit_id")
            old = current[current["Student_ID"] == selected_id].iloc[0]
            with st.form("edit_student_form"):
                e1, e2 = st.columns(2)
                edit_name = e1.text_input("Student name", value=old["Student_Name"])
                edit_dept = e2.text_input("Department", value=old["Department"])
                edit_total = e1.number_input("Total working days", min_value=0, step=1, value=int(old["Total_Days"]))
                edit_present = e2.number_input("Present days", min_value=0, step=1, value=int(old["Present_Days"]))
                edit_submit = st.form_submit_button("Save edits")
            if edit_submit:
                if not edit_name.strip() or not edit_dept.strip():
                    st.error("Student name and department cannot be blank.")
                elif edit_present > edit_total:
                    st.error("Present days cannot be greater than total working days.")
                else:
                    changed = current[REQUIRED_COLUMNS].copy()
                    mask = changed["Student_ID"] == selected_id
                    changed.loc[mask, ["Student_Name", "Department", "Total_Days", "Present_Days"]] = [
                        edit_name.strip(), edit_dept.strip(), int(edit_total), int(edit_present)
                    ]
                    save_changes(changed, "Student record updated.")
                    st.rerun()

    with st.expander("🗑️ Delete a student"):
        current = st.session_state.attendance_df
        if current.empty:
            st.info("There are no records to delete.")
        else:
            delete_id = st.selectbox("Choose Student ID to delete", current["Student_ID"].tolist(), key="delete_id")
            confirm_delete = st.checkbox(f"Confirm deletion of Student ID {delete_id}", key="confirm_delete")
            if st.button("Delete selected student", type="secondary"):
                if not confirm_delete:
                    st.error("Please tick the confirmation box first.")
                else:
                    changed = current.loc[current["Student_ID"] != delete_id, REQUIRED_COLUMNS]
                    save_changes(changed, "Student deleted.")
                    st.rerun()


elif page == "Attendance Calculator":
    st.subheader("Attendance Calculator")
    st.write("Enter the number of working days and days present. The application calculates absences and attendance percentage.")
    with st.form("calculator_form"):
        c1, c2 = st.columns(2)
        total = c1.number_input("Total working days", min_value=0, step=1, value=100)
        present = c2.number_input("Present days", min_value=0, step=1, value=80)
        calculate = st.form_submit_button("Calculate attendance")
    if calculate:
        if present > total:
            st.error("Present days cannot be greater than total working days.")
        else:
            absent = int(total - present)
            percentage = (present / total * 100) if total > 0 else 0
            status = category_for(percentage)
            x, y, z = st.columns(3)
            x.metric("Absent Days", absent)
            y.metric("Attendance", f"{percentage:.2f}%")
            z.metric("Status", status)
            st.info("Formula: (Present Days ÷ Total Working Days) × 100. When total working days are zero, attendance is shown as 0% to avoid division by zero.")


elif page == "Data Analysis":
    st.subheader("Data Analysis with Pandas")
    if df.empty:
        st.info("Upload or add student data to see analysis.")
    else:
        values = df["Attendance_Percentage"]
        a, b, c = st.columns(3)
        a.metric("Average attendance", f"{values.mean():.2f}%")
        b.metric("Highest attendance", f"{values.max():.2f}%")
        c.metric("Lowest attendance", f"{values.min():.2f}%")
        st.markdown("### Category counts")
        counts = df["Category"].value_counts().reindex(["Excellent", "Good", "Low", "Critical"], fill_value=0)
        st.dataframe(counts.rename_axis("Category").reset_index(name="Students"), use_container_width=True, hide_index=True)
        st.markdown("### Students below 75%")
        low = df[df["Attendance_Percentage"] < 75].sort_values("Attendance_Percentage")
        st.dataframe(format_table(low[["Student_ID", "Student_Name", "Attendance_Percentage", "Absent_Days"]]), use_container_width=True, hide_index=True)
        st.markdown("### Data-based insights")
        st.write(f"- The dataset contains **{len(df)}** student record(s).")
        st.write(f"- **{len(low)}** student(s) are below the 75% attendance threshold.")
        st.write(f"- **{int((df['Category'] == 'Excellent').sum())}** student(s) have attendance of at least 90%.")
        st.write(f"- The difference between highest and lowest attendance is **{values.max() - values.min():.2f} percentage points**.")
        st.caption("All values above are calculated from the currently loaded dataset using Pandas.")


elif page == "Visualizations":
    st.subheader("Visualizations with Matplotlib")
    if df.empty:
        st.info("No data available for charting.")
    else:
        st.markdown("### Individual student attendance")
        plot_df = df.sort_values("Student_ID")
        fig, ax = plt.subplots(figsize=(11, 4.8))
        bars = ax.bar(plot_df["Student_ID"].astype(str), plot_df["Attendance_Percentage"])
        ax.axhline(75, linestyle="--", linewidth=1.5, label="75% threshold")
        ax.set_title("Attendance Percentage by Student")
        ax.set_xlabel("Student ID")
        ax.set_ylabel("Attendance (%)")
        ax.set_ylim(0, 105)
        ax.tick_params(axis="x", rotation=45)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("### Attendance category distribution")
        counts = df["Category"].value_counts().reindex(["Excellent", "Good", "Low", "Critical"], fill_value=0)
        counts = counts[counts > 0]
        if counts.empty:
            st.info("There are no categories to display.")
        else:
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
            ax.set_title("Students by Attendance Category")
            ax.axis("equal")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)


elif page == "CSV Upload":
    st.subheader("Upload Attendance CSV")
    st.write("Upload a CSV with these exact required columns: " + ", ".join(REQUIRED_COLUMNS))
    sample_bytes = pd.read_csv(SAMPLE_FILE).to_csv(index=False).encode("utf-8")
    st.download_button("Download sample CSV", data=sample_bytes, file_name="attendance_data_sample.csv", mime="text/csv")
    uploaded = st.file_uploader("Choose an attendance CSV file", type=["csv"])
    if uploaded is not None:
        try:
            preview = load_and_validate_csv(uploaded)
            st.success(f"CSV validated successfully: {len(preview)} student record(s).")
            st.dataframe(format_table(preview), use_container_width=True, hide_index=True)
            if st.button("Use uploaded dataset", type="primary"):
                save_changes(preview[REQUIRED_COLUMNS], "Uploaded dataset loaded.")
                st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Unexpected upload error: {exc}")


elif page == "Reports":
    st.subheader("Attendance Reports")
    st.write("Filter records and download the current dataset as a CSV report.")
    report_df = df.copy()
    only_low = st.checkbox("Show only students below 75% attendance")
    departments = ["All"] + sorted(report_df["Department"].dropna().unique().tolist())
    report_dept = st.selectbox("Department", departments, key="report_department")
    if only_low:
        report_df = report_df[report_df["Attendance_Percentage"] < 75]
    if report_dept != "All":
        report_df = report_df[report_df["Department"] == report_dept]
    st.dataframe(format_table(report_df[["Student_ID", "Student_Name", "Department", "Total_Days", "Present_Days", "Absent_Days", "Attendance_Percentage"]]), use_container_width=True, hide_index=True)
    report_bytes = report_df[REQUIRED_COLUMNS + ["Absent_Days", "Attendance_Percentage"]].to_csv(index=False).encode("utf-8")
    st.download_button("Download attendance report CSV", data=report_bytes, file_name="attendance_report.csv", mime="text/csv")
    st.caption("The downloaded report includes calculated absent days and attendance percentage.")




st.divider()
st.caption("AttendEase • Academic demonstration project • Python + Pandas + Matplotlib + Streamlit")
