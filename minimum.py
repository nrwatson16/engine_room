import streamlit as st

# Basic page config
st.set_page_config(page_title="Engine Room", layout="wide")

# Simple header
st.title("Engine Room")

# Test if basic functionality works
st.write("Testing basic Streamlit functionality")

# If this works, we can start adding more features
if st.button("Click me"):
    st.write("Button works!")