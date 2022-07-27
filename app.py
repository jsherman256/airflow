import streamlit as st
import pandas as pd
import numpy as np
from lib import *

with open('README.md', 'r') as readme:
    st.markdown(readme.read())

st.markdown('---')

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


# Fresh and purified air
columns = st.columns(3)
with columns[0]:
    fresh_cfm = st.number_input("Outdoor Air (CFM)", min_value=0, value=200, step=10)
with columns[1]:
    cadr = st.number_input("Purifiers (CADR)", min_value=0, value=0, step=10)
total_cfm = (fresh_cfm + cadr)

# Flow and air changes
total_ach = 60 * (total_cfm / room_volume)
fresh_ach = 60 * (fresh_cfm / room_volume)
fresh_cfm_per_person = fresh_cfm / people

# Results
st.markdown("---")

ashrae_values = ashrae.loc[room_type]
ashrae_cfm = (ashrae_values['cfm/p'] * people) + (ashrae_values['cfm/ft2'] * length * width)

co2_predictions = (
    pd
    .DataFrame
    .from_dict(
        {t: co2_by_time(t, co2_cubic_meter_per_hour, people, fresh_ach, f3_to_m3(room_volume), co2_outdoor) for t in np.arange(0, 2, 0.05)},
        orient='index',
        columns=['CO2']
    )
)

# Calculate possible errors and warnings

warnings = []
errors = []

if fresh_cfm < ashrae_cfm:
    errors.append(f"ASHRAE recommends a bare minimum of **{round(ashrae_cfm)} CFM of outdoor air** for this room. Consider more ventilation or fewer occupants.")

if total_ach < 3:
    errors.append("Fewer than **3 air changes per hour** increases the risk of COVID spread")
elif total_ach < 6:
    warnings.append("You can reduce COVID transmission risk by bringing in **6+ ACH** of outdoor air")

if co2_predictions.CO2.max() > 1000:
    errors.append("The CO2 levels in this room are above recommended limits. Bring in more outdoor air. Aim for **< 800 ppm**")
elif co2_predictions.CO2.max() > 800:
    warnings.append("The CO2 levels in this room are a bit high. Bring in more outdoor air. Aim for **< 800 ppm**")

for e in errors:
    st.error(e)
for w in warnings:
    st.warning(w)

columns = st.columns(4)
with columns[0]:
    st.metric("Total ACH", round(total_ach))
with columns[1]:
    st.metric("Outdoor ACH", round(fresh_ach))
with columns[2]:
    st.metric("Outdoor CFM/person", round(fresh_cfm_per_person))
with columns[3]:
    st.metric("99.9% clearance", f"{clearance_time_999(total_ach)} min")

# Graph
if fresh_cfm > 0:
    st.markdown("#### Predicted CO2 over time")
    st.line_chart(
        co2_predictions
    )