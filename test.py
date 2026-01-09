import streamlit as st

st.title("Accidents")
st.write("Hi")
td = st.number_input("Traffic density", min_value=0, max_value=100)
v = st.number_input("Average Speed", min_value=0, max_value=120)
R = st.slider("Rain factor", 0.0, 1.0, 0.6)

S = 5 * (td*v+R+1)
st.write(f"Risk: {S}")