import streamlit as st
import pandas as pd
from lib import clearance_time_99

# Room type and occupancy
ashrae = pd.read_csv('ASHRAE.csv', index_col=0)
columns = st.columns([2,1])
with columns[0]:
    room_type = st.selectbox("Type of room:", ashrae.index)
with columns[1]:
    people = st.number_input("Number of people:", min_value=1, value=20)
    
# Room size
columns = st.columns(3)
with columns[0]:
    length = st.number_input("Room length (ft):", value=15)
with columns[1]:
    width = st.number_input("Room width (ft):", value=15)
with columns[2]:
    ceiling = st.number_input("Ceiling height (ft):", value=8)
room_volume = (length * width * ceiling)

st.markdown("---")

import numpy as np

ashrae_values = ashrae.loc[room_type]
ashrae_cfm = (ashrae_values['cfm/p'] * people) + (ashrae_values['cfm/ft2'] * length * width)
ashrae_cfm_per_person = int(ashrae_cfm / people)
ashrae_ach = 60 * ashrae_cfm / room_volume

lps_cfm = 2.11888 * 10 * people
lps_cfm_per_person = lps_cfm / people
lps_ach = 60 * lps_cfm / room_volume

six_ach_cfm = 6 * room_volume / 60
six_ach_cfm_per_person = (6 * room_volume / 60) / people

twelve_ach_cfm = 12 * room_volume / 60
twelve_ach_cfm_per_person = (12 * room_volume / 60) / people

results = pd.DataFrame(
    np.array([
        [ashrae_cfm, ashrae_cfm_per_person, ashrae_ach, clearance_time_99(ashrae_ach)],
        [lps_cfm, lps_cfm_per_person, lps_ach, clearance_time_99(lps_ach)],
        [six_ach_cfm, six_ach_cfm_per_person, 6, clearance_time_99(6)],
        [twelve_ach_cfm, twelve_ach_cfm_per_person, 12, clearance_time_99(12)],
    ]),
    dtype='int',
    columns = ['Total CFM', 'CFM per person', 'ACH', '99% Clearance (minutes)'],
    index=['ASHRAE Standard 62.1', '10 L/s/p', '6 ACH', '12 ACH']
)

st.table(results)

st.markdown("### ASHRAE Standard 62.1")

st.markdown(f"**ASHRAE Standard 62.1** recommends a *bare minimum* of **{int(ashrae_cfm)} CFM** for this room (**{int(ashrae_cfm_per_person)} CFM** per person)")
st.markdown(f"That would provide **{int(ashrae_ach)} ACH**, clearing 99% of particles in **{clearance_time_99(ashrae_ach)} minutes**.")


st.markdown("### 10 Liters per second")

st.markdown("Studies indicate 10 L/s per person of ventilation provides better protection from COVID than ASHRAE Standards do.")
st.markdown(f"Using this metric, this room would require **{int(lps_cfm)} CFM** for this room (**{int(lps_cfm/people)} CFM** per person).")
st.markdown(f"That would provide **{int(lps_ach)} ACH**, clearing 99% of particles in **{clearance_time_99(lps_ach)} minutes**.")

st.markdown("### 6 Air Changes per Hour")
six_ach_cfm = 6 * room_volume / 60
st.markdown(f"Providing 6 ACH would require **{int(six_ach_cfm)} CFM** for this room (**{int(six_ach_cfm/people)} CFM** per person)")
st.markdown(f"It would take **{int(clearance_time_99(6))} minutes** to clear 99% of particles.")

st.markdown("### 12 Air Changes per Hour")
twelve_ach_cfm = 12 * room_volume / 60
st.markdown(f"Providing 12 ACH would require **{int(twelve_ach_cfm)} CFM** for this room (**{int(twelve_ach_cfm/people)} CFM** per person)")
st.markdown(f"It would take **{int(clearance_time_99(12))} minutes** to clear 99% of particles.")

st.table(ashrae)