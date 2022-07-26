import streamlit as st
import pandas as pd
from math import exp
import numpy as np

def cfm_to_lps(cfm):
    return cfm * 0.47194745

# cubic feet to cubic meters
def f3_to_m3(f3):
    return f3 * 0.0283168

# Time to clear 99% of particles
def clearance_time_99(ach):
    if ach == 0:
        return "∞"
    return int((np.log(100) / ach) * 60)

# Time to clear 99.9% of particles
def clearance_time_999(ach):
    if ach == 0:
        return "∞"
    return int((np.log(1000) / ach) * 60)

co2_cubic_meter_per_hour = 0.05
co2_outdoor = 0.000420

def co2_by_time(t, co2_rate, people, ach, volume, co2_init):
    q = co2_rate
    n = ach
    V = volume

    result = (q*people / (n * V)) * (1 - (1 / exp(n * t)))
    result += ((co2_init - co2_outdoor) * (1 / exp(n*t)))
    result += co2_outdoor
    
    # Retun in ppm
    return result * 1000000


# Room size
columns = st.columns(4)
with columns[0]:
    length = st.number_input("Room length (feet):", value=15)
with columns[1]:
    width = st.number_input("Room width (feet):", value=15)
with columns[2]:
    ceiling = st.number_input("Ceiling height (feet):", value=8)
with columns[3]:
    room_volume = (length * width * ceiling)
    st.metric("Room Volume (cubic feet)", room_volume)

# Occupants
columns = st.columns([1,2,1])
with columns[0]:
    people = st.number_input("Number of people:", min_value=1, value=20)

# Fresh and purified air
columns = st.columns(4)
with columns[0]:
    fresh_cfm = st.number_input("Fresh Air (CFM)", min_value=0, value=0, step=10)
with columns[1]:
    cadr = st.number_input("Purifiers (CADR)", min_value=0, value=0, step=10)
with columns[3]:
    total_cfm = (fresh_cfm + cadr)
    st.metric("Total CFM", total_cfm)

# Flow and air changes
ach = 60 * (total_cfm / room_volume)
liters_per_second = cfm_to_lps(total_cfm) 
lps_per_person = liters_per_second / people

# Results
st.markdown("---")
columns = st.columns(4)
with columns[0]:
    st.metric("Air Changes per Hour", round(ach, 1))
with columns[1]:
    st.metric("L/s per person", round(lps_per_person, 1))
with columns[2]:
    st.metric("99% clearance", f"{clearance_time_99(ach)} min")
with columns[3]:
    st.metric("99.9% clearance", f"{clearance_time_999(ach)} min")

# Graph
if fresh_cfm > 0:
    st.line_chart(
        pd
        .DataFrame
        .from_dict(
            {t: co2_by_time(t, co2_cubic_meter_per_hour, people, 60 * (fresh_cfm / room_volume), f3_to_m3(room_volume), co2_outdoor) for t in np.arange(0, 2, 0.05)},
            orient='index',
            columns=['CO2']
        )
    )