import streamlit as st
import pandas as pd

ashrae = pd.read_csv('ASHRAE.csv', index_col=0)
st.dataframe(ashrae)



left, center, right = st.columns(3)
with left:
    room = st.selectbox("Type of room:", ashrae.index)
with center:
    people = st.number_input("Number of people:", min_value=1, value=20)
with right:
    size = st.number_input("Room size (square feet):", value=100)

values = ashrae.loc[room]
cfm = (values['cfm/p'] * people) + (values['cfm/ft2'] * size)
ach = cfm / size
st.markdown("---")
st.markdown(f"### Minimum of {int(cfm)} CFM recommended ({int(ach)} ACH)")