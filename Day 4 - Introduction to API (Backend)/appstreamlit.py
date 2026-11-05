import streamlit as st
st.title("Streamlit Application")
st.write("Implementation of Streamlit")
import streamlit as st

st.title("This is a Student Application")
st.header("This is a School Data")
st.subheader("This is a Section")
st.write("This is Student Information.")
st.markdown("Confidential Information.")  
name = st.text_input ("Enter Your Name")
age = st.number_input("Enter Your Age")
st.write("Hello", name, "Your Age is ", age)
if st.button ("Click Me"):
 st.write ("Information Updated")
 number = st.slider("Pick a Number", 0, 100)
 st.write ("You picked",number)
