import streamlit as st

# Basic page config must come first
st.set_page_config(page_title="Engine Room", layout="wide")

# Import other required libraries
import requests
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
import os
import urllib3
import calendar
from calendar import monthcalendar, month_name

# Disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Strava API settings
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"

# Simple header
st.title("Engine Room")

# Basic Strava connection test
if 'strava_token' not in st.session_state:
    try:
        auth_link = f"{STRAVA_AUTH_URL}?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri=http://localhost:8501&scope=activity:read_all"
        st.markdown(f"[Connect to Strava]({auth_link})")
        
        code = st.text_input("Enter the code from the redirect URL:")
        if code:
            st.write("Got the code, attempting to connect...")
    except Exception as e:
        st.error(f"Error setting up Strava connection: {str(e)}")

# If this basic version works, we'll add more functionality
if st.button("Test Connection"):
    st.write("Basic setup is working!")
