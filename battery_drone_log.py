import streamlit as st
import pandas as pd
from datetime import datetime
import re
import dropbox
from io import BytesIO
import plotly.express as px


# --- Dropbox setup ---
DROPBOX_ACCESS_TOKEN = "sl.u.AFxJte7w0pP7Ec3cq-RqwnYKUnZTyC9Q2jX8UVnSSWSKBlYhzm3eczFaMJM8upTWuFZd19P1uTNQ-stZb-k9QjTuLYWOFq92WRkHkJjjrJl7Mt1oFp4M3cSjNEXsP8kzcx7hZCkMPGbro5xvAvo3qp3iv-sh0BW_mSJ47CWJ_b6V1iwbLLlJEnyfDPt0REE_Ze5kBn7mVsrZN2WUOeUrYv0D9QBWMMIyROZcG0JvGX9pxxSicv_ZYTOZT5VQ8sILhWVyCBUlt6i3Og21TXDLbe4x6cCwIwMXKlmShDfzfMhnOgAv7KwXfeeYE4mjFhofWW-FfPHXlrcOzXz-afomeibo5Jf8K7gisW8jpcL96jyJBv3dnesCnXyxXaMxcql83T2Ghq0BB2IILKgYKbmZ01PvZQFp33Wh1kjoNDxQ855hMLInJFz_HyfWDC3T7RmPoYOAgnYJp_as557h8EXc-lsQczBEjdKfh-Z1SEKKM5JasTrOHYRcdJYKJTpsAi7I1LoU_oxKobuE44l3hCOnqhnkCbcoJ28IN3AYFWidXAJ5RlhGXoMmfA0-QGim5ibmYQTgA0W3X4aAzfj2BzoVs0sd-Vfl9guHhtksqzEnsscDcO6FeNMiWkqLShp6o-sFrdw7eE5ZUq8Kim5jSmt3YMx2MGmKaHw2tk7oIckT5KmSEHiWz6xerJ-JCKvE3bumbMTxmN9J96_XtbwOENtjPjJOqO65MSg_7cg-8Hm4C3CmNtpYjDTYPt1Aue6gMoouMYSWCJs4gi6S39w5gP-h3v4Ni9pvnioFepoGQzYn6hRexkxenPG3CJqk79xhesnxKXPWZ7bgo_GpSS21R20RncjnATUpP0bSmakINty7vuTyThZApsev4SC8rc8JGEgOtRRYIyhBcNsx8CtEb32b596UFQAJCrE3WiqQAItMTjI0kc6urvT1qD0NbcF9_60LiQ5rH7Hv4U5lfxh2ab3OhN9eFsGz1Ben71ZPkUs-shIQN5_Sae4PZRzCgP0nMpCWNHn5DJnkRiD1T-h5URLQ0n1xdw2dhv2yC1Z2ttChWDBYO4BijkRWD2ffWPlBiZZc-m1Bf0HxB8fqy0RqO7q4jQYXSB_PlnHnFgRZxKO1onfeVTydtPfERErA-_GWmZldtjdgbLh-x69O0SuIDJJE-ruKyaFZeBMTaKzJYenyNQgoZoyKidHaNJabqrAmW5dRWQdkjYhQFIGufh50LxMu3tJiNbZrThRs0eyPofX_AIz7V6F_OBkuTtaqtqmBN9FeAdB9UqlDTgH_cDQbA_XZHH5HT55zJZRgH4rBvbal87HyVYK6hUAaOx_IzUO5EEa6yvUpdgeM7RFfqMMaWhbg__Tp"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
# --- Load & Save Functions for Battery ---
BATTERY_XLSX_PATH = "/UseLogs/BatteryLogs.xlsx"
DRONE_XLSX_PATH = "/UseLogs/DroneLogs.xlsx"

# --- Streamlit UI ---
st.set_page_config(page_title="Battery & Drone Logger", page_icon="📝", layout="centered")
st.title("📝 Battery & Drone Logger")

# --- Tabs ---
tabs = st.tabs(["🔋 Battery Logger", "🚁 Drone Logger"])

# --- Battery Logger Tab ---
with tabs[0]:
    st.subheader("Register a New Battery Charge")

    # --- Form to Register Charge ---
    with st.form("carga_form"):
        battery_id = st.text_input("Battery ID", max_chars=20)
        start_time_str = st.text_input("Start Time (HH:MM)", placeholder="e.g. 14:30")
        duration = st.number_input("Duration (in minutes)", min_value=1)
        submit = st.form_submit_button("Save Charge")


    def load_battery_data():
        try:
            _, res = dbx.files_download(BATTERY_XLSX_PATH)
            return pd.read_excel(BytesIO(res.content))
        except dropbox.exceptions.ApiError:
            return pd.DataFrame(columns=["timestamp", "battery_id", "start_time", "duration_minutes"])
        

    def save_battery_data(df):
        with BytesIO() as f:
            df.to_excel(f, index=False)
            f.seek(0)
            dbx.files_upload(f.read(), BATTERY_XLSX_PATH, mode=dropbox.files.WriteMode.overwrite)


    if submit:
        if battery_id.strip() == "":
            st.warning("Battery ID cannot be empty.")
        else:
            today = datetime.now().date()
            start_datetime = datetime.combine(today, datetime.strptime(start_time_str, "%H:%M").time())
            new_record = {
                "timestamp": datetime.now().isoformat(),
                "battery_id": battery_id,
                "start_time": start_datetime.isoformat(),
                "duration_minutes": duration
            }
            df = load_battery_data()
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            save_battery_data(df)
            st.success("✅ Charge registered successfully.")
            st.rerun()

    # --- Show Battery Data ---
    df = load_battery_data()

    st.subheader("📋 Last 5 Charges Registered")
    if df.empty:
        st.info("No charges registered yet.")
    else:
        st.dataframe(df.sort_values(by="timestamp", ascending=False).head(5))

    st.subheader("📊 Battery Statistics")
    if not df.empty:
        count_stats = df['battery_id'].value_counts().rename_axis('battery_id').reset_index(name='total_charges')
        st.markdown("#### 🔢 Total Charges per Battery")
        st.bar_chart(count_stats.set_index('battery_id'))

        minutes_stats = df.groupby('battery_id')['duration_minutes'].sum().reset_index()
        st.markdown("#### ⏱️ Total Minutes Charged per Battery")
        st.bar_chart(minutes_stats.set_index('battery_id'))

    # --- Delete Battery Records ---
    st.subheader("🗑️ Delete Battery Records")
    if not df.empty:
        battery_ids = df['battery_id'].unique().tolist()
        with st.form("delete_form"):
            selected_id = st.selectbox("Select Battery ID to Delete", battery_ids)
            confirm = st.checkbox("I confirm I want to delete this battery's records permanently.")
            delete_submit = st.form_submit_button("Delete Battery Records")

        if delete_submit:
            if confirm:
                original_count = len(df)
                df = df[df['battery_id'] != selected_id]
                save_battery_data(df)
                st.success(f"✅ Deleted all records for battery ID `{selected_id}` ({original_count - len(df)} removed).")
                st.rerun()
            else:
                st.warning("☝️ You must confirm the deletion.")

# --- Drone Logger Tab ---
with tabs[1]:

    def load_drone_data():
        try:
            _, res = dbx.files_download(DRONE_XLSX_PATH)
            return pd.read_excel(BytesIO(res.content))
        except dropbox.exceptions.ApiError:
            return pd.DataFrame(columns=["timestamp", "battery_id", "drone_id", "start_time", "end_time", "num_locations"])
        
    def save_drone_data(drone_df):
        with BytesIO() as f:
            drone_df.to_excel(f, index=False)
            f.seek(0)
            dbx.files_upload(f.read(), DRONE_XLSX_PATH, mode=dropbox.files.WriteMode.overwrite)

    st.header("🛩️ Drone Flight Logger")

    # Form to register drone flight
    with st.form("drone_flight_form"):
        battery_id = st.text_input("Battery ID Used", max_chars=20)
        drone_id = st.text_input("Drone ID", max_chars=20)

        # Remove leading zeros and convert to an integer
        if drone_id: # Ensure the string is not empty
            drone_id = drone_id.lstrip('0')


        start_time_str = st.text_input("Start Time (HH:MM)", placeholder="e.g. 14:30")
        end_time_str = st.text_input("End Time (HH:MM)", placeholder="e.g. 15:45")
        num_locations = st.number_input("Number of Locations Visited", min_value=1, step=1)

        drone_submit = st.form_submit_button("Log Flight")

    # --- Show Battery Data ---
    drone_df = load_drone_data()

    # Validation and saving
    if drone_submit:
        time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        if not re.match(time_pattern, start_time_str):
            st.error("⛔ Invalid Start Time. Please use HH:MM format.")
        elif not re.match(time_pattern, end_time_str):
            st.error("⛔ Invalid End Time. Please use HH:MM format.")
        elif battery_id.strip() == "" or drone_id.strip() == "":
            st.warning("Battery ID and Drone ID cannot be empty.")
        else:
            # Parse times into time objects
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            today = datetime.now().date()
            start_datetime = datetime.combine(today, start_time)
            end_datetime = datetime.combine(today, end_time)

            drone_record = {
                "timestamp": datetime.now().isoformat(),
                "battery_id": battery_id,
                "drone_id": drone_id,
                "start_time": start_datetime.isoformat(),
                "end_time": end_datetime.isoformat(),
                "num_locations": num_locations
            }

            drone_df = load_drone_data()
            drone_df = pd.concat([drone_df, pd.DataFrame([drone_record])], ignore_index=True)
            save_drone_data(drone_df)

            st.success("✅ Drone flight logged successfully.")


    st.subheader("📊 Drone Flight Statistics")
    if not drone_df.empty:

        # Convert start/end time and calculate duration in minutes
        drone_df['start_dt'] = pd.to_datetime(drone_df['start_time'])
        drone_df['end_dt'] = pd.to_datetime(drone_df['end_time'])
        drone_df['duration_min'] = (drone_df['end_dt'] - drone_df['start_dt']).dt.total_seconds() / 60

        # Round duration and locations to integers for cleaner plots
        drone_df['duration_min'] = drone_df['duration_min'].fillna(0).round().astype(int)
        drone_df['num_locations'] = drone_df['num_locations'].fillna(0).astype(int)

        def clean_drone_id(drone_id):
            drone_id = str(drone_id).strip()  # quitar espacios
            if drone_id.isdigit():
                return str(int(drone_id))  # quitar ceros a la izquierda
            return drone_id

        drone_df['drone_id'] = drone_df['drone_id'].apply(clean_drone_id)
        flight_time_per_drone = drone_df.groupby("drone_id")["duration_min"].sum().reset_index()
        st.markdown("#### ⏱️ Total Flight Time per Drone (in Minutes)")
        fig = px.bar(
            flight_time_per_drone,
            x="drone_id",
            y="duration_min",
            color="drone_id",  # Different color per drone
            labels={"drone_id": "Drone ID", "duration_min": "Flight Time (min)"}
        )
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        total_locations_per_drone = drone_df.groupby("drone_id")["num_locations"].sum().reset_index()
        st.markdown("#### 📍 Total Locations Visited per Drone")
        fig = px.bar(
            total_locations_per_drone,
            x="drone_id",
            y="num_locations",
            color="drone_id",  # Different color per drone
            labels={"drone_id": "Drone ID", "num_locations": "Total Locations"}
        )
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # --- Delete Drone Records ---
    st.subheader("🗑️ Delete Drone Records")
    if not drone_df.empty:
        drone_ids = drone_df['drone_id'].dropna().unique().tolist()
        with st.form("delete_drone_form"):
            selected_drone_id = st.selectbox("Select Drone ID to Delete", drone_ids)
            confirm_drone = st.checkbox("I confirm I want to delete this drone's records permanently.")
            delete_drone_submit = st.form_submit_button("Delete Drone Records")

        if delete_drone_submit:
            if confirm_drone:
                original_count = len(drone_df)
                drone_df = drone_df[drone_df['drone_id'] != selected_drone_id]
                try:
                    save_drone_data(drone_df)
                    st.success(f"✅ Deleted all records for drone ID `{selected_drone_id}` ({original_count - len(drone_df)} removed).")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to save updated data: {e}")
            else:
                st.warning("☝️ You must confirm the deletion.")