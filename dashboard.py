import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from database.db import create_table, create_default_user, validate_user, insert_log, fetch_logs

MODEL_PATH = "models/power_model.pkl"
TARIFF = 8
OVERLOAD_THRESHOLD = 1000

create_table()
create_default_user()

st.set_page_config(page_title="Smart Energy Monitor", layout="wide")

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["Time","Voltage","Current","Energy","Power","Cost","Status"]
    )


# ---------------- LOGIN ----------------

def login_page():

    st.title("Energy Monitoring Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if validate_user(username,password):
            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("Invalid credentials")


# ---------------- DASHBOARD ----------------

def dashboard_page():

    st.title("Smart Energy Monitor Dashboard")

    col1,col2 = st.columns(2)

    voltage = col1.number_input("Voltage",value=230.0)
    current = col2.number_input("Current",value=1.0)

    energy = (voltage * current) / 1000

    model = joblib.load(MODEL_PATH)

    input_df = pd.DataFrame({
        "Voltage":[voltage],
        "Current":[current],
        "Energy":[energy]
    })

    power = model.predict(input_df)[0]

    cost = energy * TARIFF

    status = "Normal"

    if power > OVERLOAD_THRESHOLD:
        status = "Overload"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = pd.DataFrame({
        "Time":[timestamp],
        "Voltage":[voltage],
        "Current":[current],
        "Energy":[energy],
        "Power":[power],
        "Cost":[cost],
        "Status":[status]
    })

    st.session_state.history = pd.concat(
        [st.session_state.history,new_row],
        ignore_index=True
    )

    insert_log(voltage,current,energy,power,status)

    col1,col2,col3 = st.columns(3)

    col1.metric("Predicted Power (W)",round(power,2))
    col2.metric("Energy (kWh)",round(energy,3))
    col3.metric("Estimated Cost (₹)",round(cost,2))

    if status == "Overload":
        st.error("High Power Usage Detected")

    st.subheader("Power Trend")

    st.line_chart(st.session_state.history["Power"])

    st.subheader("Session Data")

    st.dataframe(st.session_state.history)


# ---------------- ANALYTICS ----------------

def analytics_page():

    st.title("Energy Analytics")

    df = st.session_state.history

    if len(df) == 0:
        st.write("No data available")
        return

    st.subheader("Power Trend")
    st.line_chart(df["Power"])

    st.subheader("Energy Consumption")
    st.bar_chart(df["Energy"])

    st.subheader("Cost Trend")
    st.line_chart(df["Cost"])

    avg_power = df["Power"].mean()
    max_power = df["Power"].max()
    min_power = df["Power"].min()

    col1,col2,col3 = st.columns(3)

    col1.metric("Average Power",round(avg_power,2))
    col2.metric("Max Power",round(max_power,2))
    col3.metric("Min Power",round(min_power,2))


# ---------------- ALERTS ----------------

def alerts_page():

    st.title("Alerts")

    df = st.session_state.history

    alerts = df[df["Status"]=="Overload"]

    if len(alerts)==0:
        st.success("No alerts detected")

    else:
        st.error("Overload Events Detected")
        st.dataframe(alerts)


# ---------------- SENSOR MONITOR ----------------

def sensor_monitor_page():

    st.title("Sensor Monitor")

    logs = fetch_logs()

    if len(logs)==0:
        st.write("No sensor data available")
        return

    df = pd.DataFrame(
        logs,
        columns=["ID","Voltage","Current","Energy","Power","Status","Time"]
    )

    st.subheader("Recent Sensor Logs")

    st.dataframe(df.tail(100))

    st.subheader("Voltage Trend")
    st.line_chart(df["Voltage"])

    st.subheader("Current Trend")
    st.line_chart(df["Current"])

    st.subheader("Power Trend")
    st.line_chart(df["Power"])


# ---------------- ENERGY HISTORY ----------------

def energy_history_page():

    st.title("Energy History")

    df = st.session_state.history

    if len(df)==0:
        st.write("No data available")
        return

    today_energy = df["Energy"].sum()
    today_bill = today_energy * TARIFF
    monthly_prediction = today_energy * 30 * TARIFF

    col1,col2,col3 = st.columns(3)

    col1.metric("Today's Energy (kWh)",round(today_energy,2))
    col2.metric("Today's Bill (₹)",round(today_bill,2))
    col3.metric("Predicted Monthly Bill (₹)",round(monthly_prediction,2))

    st.subheader("Daily Usage")

    daily = df.copy()
    daily["Date"] = pd.to_datetime(daily["Time"]).dt.date

    daily_summary = daily.groupby("Date")["Energy"].sum().reset_index()
    daily_summary["Bill"] = daily_summary["Energy"] * TARIFF

    st.dataframe(daily_summary)


# ---------------- REPORTS ----------------

def report_page():

    st.title("Reports")

    df = st.session_state.history

    if len(df)==0:
        st.write("No data available")
        return

    today_energy = df["Energy"].sum()
    today_bill = today_energy * TARIFF
    monthly_prediction = today_energy * 30 * TARIFF

    alerts = df[df["Status"]=="Overload"]

    # ENERGY REPORT

    energy_report = ""

    energy_report += "SMART ENERGY MONITOR REPORT\n"
    energy_report += "="*50 + "\n\n"

    energy_report += f"Generated On : {datetime.now()}\n\n"

    energy_report += "-"*50 + "\n"
    energy_report += "TODAY SUMMARY\n"
    energy_report += "-"*50 + "\n\n"

    energy_report += f"Energy Used        : {today_energy:.2f} kWh\n"
    energy_report += f"Today's Bill       : ₹{today_bill:.2f}\n\n"

    energy_report += "-"*50 + "\n"
    energy_report += "MONTHLY PREDICTION\n"
    energy_report += "-"*50 + "\n\n"

    energy_report += f"Predicted Monthly Bill : ₹{monthly_prediction:.2f}\n\n"

    energy_report += "-"*50 + "\n"
    energy_report += "OVERLOAD EVENTS\n"
    energy_report += "-"*50 + "\n\n"

    if len(alerts)==0:
        energy_report += "No overload events detected\n"
    else:
        for _,row in alerts.iterrows():
            energy_report += f"{row['Time']}  |  Power: {row['Power']:.2f} W\n"

    st.download_button(
        "Download Energy Report",
        energy_report,
        file_name="energy_report.txt"
    )

    # DAILY HISTORY

    daily = df.copy()
    daily["Date"] = pd.to_datetime(daily["Time"]).dt.date

    daily_summary = daily.groupby("Date")["Energy"].sum().reset_index()
    daily_summary["Bill"] = daily_summary["Energy"] * TARIFF

    daily_txt = ""

    daily_txt += "DAILY ENERGY HISTORY\n"
    daily_txt += "="*50 + "\n\n"

    daily_txt += "Date          Energy(kWh)     Bill(₹)\n"
    daily_txt += "-"*40 + "\n"

    for _,row in daily_summary.iterrows():
        daily_txt += f"{row['Date']}     {row['Energy']:.2f}          {row['Bill']:.2f}\n"

    st.download_button(
        "Download Daily History",
        daily_txt,
        file_name="daily_history.txt"
    )

    # SENSOR LOGS

    sensor_txt = ""

    sensor_txt += "SENSOR DATA LOG\n"
    sensor_txt += "="*60 + "\n\n"

    sensor_txt += "Time                Voltage   Current   Energy   Power   Cost   Status\n"
    sensor_txt += "-"*70 + "\n"

    for _,row in df.iterrows():

        sensor_txt += (
            f"{row['Time']}   "
            f"{row['Voltage']}   "
            f"{row['Current']}   "
            f"{row['Energy']:.2f}   "
            f"{row['Power']:.2f}   "
            f"{row['Cost']:.2f}   "
            f"{row['Status']}\n"
        )

    st.download_button(
        "Download Sensor Logs",
        sensor_txt,
        file_name="sensor_logs.txt"
    )


# ---------------- MAIN ----------------

if st.session_state.logged_in:

    menu = st.sidebar.selectbox(
        "Navigation",
        [
            "Dashboard",
            "Analytics",
            "Alerts",
            "Sensor Monitor",
            "Energy History",
            "Reports",
            "Logout"
        ]
    )

    if menu == "Dashboard":
        dashboard_page()

    elif menu == "Analytics":
        analytics_page()

    elif menu == "Alerts":
        alerts_page()

    elif menu == "Sensor Monitor":
        sensor_monitor_page()

    elif menu == "Energy History":
        energy_history_page()

    elif menu == "Reports":
        report_page()

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

else:
    login_page()