import streamlit as st
import pandas as pd
from datetime import datetime
import re
import dropbox
from io import BytesIO
import plotly.express as px


# --- Dropbox setup ---
DROPBOX_ACCESS_TOKEN = "sl.u.AFzZC_D4ke8rxplRv1eAC1Q7O-vDAYjeVhM9-wVJyRwwytzDv6gcL62YPkFR5faBHWX7mRZFWuaQ3D_p006Rxoyg01PF7Cr5O1KYrsQfnvzsUBrLCJO72nIgjy5ZX3pK_N50sZ13_wb70L0BA1MilTDluADN_N5zYrPFTJo2Qd_EW0L4Zi27cb1f9dDRMlAgIj4SA7YSkAkdv8_DS-dz7tyt6BiGkiNb22zzgMS53QFn4FurC4MPvj0KQPSkMS6oErCfN2Hbx9O3oDZ5hvTR6xNCGEArKEcYQZoRlstruTBkw2m-nKOfd3ZncL1YIAOmBdF8anST7aSxRWJL1BuTUkQxFmTmnGVvHqQ3sFG0vPhykV4PebVIhf02GpXIzxBt2sgZCLFajXhU_iKZlW1dWvep-n1W3Ac-22ALG0QOaHGlOpgjqsx5yDMZ2CHhNihsDEJuI8ntuQGRKiRXVMulYsSPLAkerpK8em3xHUzp4yDpRkZ7ityIiTcKWiOk8o0dgFOQ1dtraeiUoa76ArYetzOleinAbfrB3Ps8LGaUdijOTqArZ_8PC6WbTxZfsocQywJNWz-1OSxgSo7bRePGDCWJslHbztI1Hr724wWpUmyCDYdK2Fvk8sRM4boHBqveE-bPEPTjOKV1hYwsF_mIGyoDvcHSUkI7cO6mjzCvO1PZqQ5_KZFzVs_0Y0z17pk9nsfDFX_hofeZR_WwpEPNFl4xtGwELhzimJ-Gii7LHd-JQzMICZeHbt7X4oyethnZoHP1YQnI1FvnFKMEub1BKjNJ4pmDaghmcJmqzHa-GHU9GDNbyxXtVrBIwJpcl7n95jYdRRYkSRuYps_nsVaRKqv9NBXbxoClYbi1DCYz7JoQDBrxGE6IX76Uv2rh0qvtQGUXWDGSwD1AyNfCmaKImH9rp4kJQWxcsvPzEhMflfR3dFGG8CcYT3WkOxUN2CVpyIG61DT7V9SWpb6FTuvCkYdzbwPbqf86OfwrLEX_SpsTQ0jCIK4nJV7q2hOFlW_5x9DUkO8PkiQKlOA6ggXzxHfMQjP-CeyVlRR4EzK-ZFn3Cc0xlN3s4tyvvwpPC0F9BLNM9iPp0dlRfk1EpQQqqOmTEu0dFR8qk-7QCXrF76RI088cR3XjWV_NcGm7KDvbGPyF1yVe9SdU7QAXhzIx4Cn098M_TD-0pT8io5pqex9zf_wmIrHf2zm-yF39ux8WR6HqhIM-FgTVO30woyxc8yIRRpYUpG74r3MR45j2HHXoQkhSiAFF2F8ii1vjMbXKS6zMQYEw7_w3Pgjt7dMFkVn6bgYGZqcxO2e-rSw3tthrqK6_o69f-i1Xyx5iwSGULk28U6haW8FtPz0m0-76Zr_P"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
# --- Load & Save Functions for Battery ---
BATTERY_XLSX_PATH = "/Carpeta del equipo de Dronomy/UseLogs/BatteryLogs.xlsx"
DRONE_XLSX_PATH = "/Carpeta del equipo de Dronomy/UseLogs/DroneLogs.xlsx"

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
        
    def load_drone_data():
        try:
            _, res = dbx.files_download(DRONE_XLSX_PATH)
            return pd.read_excel(BytesIO(res.content))
        except dropbox.exceptions.ApiError:
            return pd.DataFrame(columns=["timestamp", "battery_id", "drone_id", "start_time", "end_time", "num_locations"])

    def save_battery_data(df):
        with BytesIO() as f:
            df.to_excel(f, index=False)
            f.seek(0)
            dbx.files_upload(f.read(), BATTERY_XLSX_PATH, mode=dropbox.files.WriteMode.overwrite)

    def save_drone_data(df):
        with BytesIO() as f:
            df.to_excel(f, index=False)
            f.seek(0)
            dbx.files_upload(f.read(), DRONE_XLSX_PATH, mode=dropbox.files.WriteMode.overwrite)

    if submit:
        if battery_id.strip() == "":
            st.warning("Battery ID cannot be empty.")
        else:
            today = datetime.now().date()
            start_datetime = datetime.combine(today, start_time)
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
    st.header("🛩️ Drone Flight Logger")

    # Form to register drone flight
    with st.form("drone_flight_form"):
        battery_id = st.text_input("Battery ID Used", max_chars=20)
        drone_id = st.text_input("Drone ID", max_chars=20)
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


    if not drone_df.empty:
        st.subheader("📊 Drone Flight Statistics")

        # Convert start/end time and calculate duration in minutes
        drone_df['start_dt'] = pd.to_datetime(drone_df['start_time'])
        drone_df['end_dt'] = pd.to_datetime(drone_df['end_time'])
        drone_df['duration_min'] = (drone_df['end_dt'] - drone_df['start_dt']).dt.total_seconds() / 60

        # Round duration and locations to integers for cleaner plots
        drone_df['duration_min'] = drone_df['duration_min'].fillna(0).round().astype(int)
        drone_df['num_locations'] = drone_df['num_locations'].fillna(0).astype(int)


        # --- 1. Total flight time per drone ---
        minutes_per_drone = drone_df.groupby('drone_id')['duration_min'].sum().reset_index()

        fig_minutes = px.bar(
            minutes_per_drone,
            x='duration_min',
            y='drone_id',
            orientation='h',
            color='drone_id',
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={'duration_min': 'Flight Time (min)', 'drone_id': 'Drone ID'},
            title="⏱️ Total Flight Time per Drone"
        )
        fig_minutes.update_layout(
            yaxis_title="Drone ID",
            xaxis_title="Minutes",
            yaxis=dict(tickformat="d"),
            xaxis=dict(tickformat="d"),
            height=400,
        )
        st.plotly_chart(fig_minutes, use_container_width=True)

        # --- 2. Total locations visited per drone ---
        locs_per_drone = drone_df.groupby('drone_id')['num_locations'].sum().reset_index()

        fig_locs = px.bar(
            locs_per_drone,
            x='drone_id',
            y='num_locations',
            color='drone_id',
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={'num_locations': 'Locations Visited', 'drone_id': 'Drone ID'},
            title="📍 Total Locations Visited per Drone"
        )
        fig_locs.update_layout(
            xaxis_title="Drone ID",
            yaxis_title="Locations",
            yaxis=dict(tickformat="d"), 
            xaxis=dict(tickformat="d"),
            height=400,
        )
        st.plotly_chart(fig_locs, use_container_width=True)
    
    # --- Delete Drone Records ---
    if not drone_df.empty:
        st.subheader("🗑️ Delete Drone Records")
        drone_ids = drone_df['drone_id'].unique().tolist()
        with st.form("delete_drone_form"):
            selected_id = st.selectbox("Select Drone ID to Delete", drone_ids)
            confirm = st.checkbox("I confirm I want to delete this drone's records permanently.")
            delete_submit = st.form_submit_button("Delete Drone Records")

        if delete_submit:
            if confirm:
                original_count = len(drone_df)
                drone_df = drone_df[drone_df['drone_id'] != selected_id]
                save_drone_data(drone_df)
                st.success(f"✅ Deleted all records for drone ID `{selected_id}` ({original_count - len(drone_df)} removed).")
                st.rerun()
            else:
                st.warning("☝️ You must confirm the deletion.")