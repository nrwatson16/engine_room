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



# Get the deployment URL dynamically
def get_base_url():
    if 'DEPLOYMENT_URL' in os.environ:
        return os.environ['DEPLOYMENT_URL']
    else:
        # Check if running on Streamlit Cloud
        if st._is_running_with_streamlit:
            return "https://trainingcal.streamlit.app"  # Update this to your actual app URL
        return "http://localhost:8501"

# [Your CSS stays the same]

# Simple header
st.title("Training Cal")

# Basic Strava authentication
if 'strava_token' not in st.session_state:
    try:
        base_url = get_base_url()
        auth_link = f"{STRAVA_AUTH_URL}?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={base_url}&scope=activity:read_all"
        st.write("Debug: Auth link being used:", auth_link)
        st.markdown(f"[Connect to Strava]({auth_link})")
        
        # Get the code from URL params if present
        query_params = st.experimental_get_query_params()
        code = query_params.get("code", [None])[0]
        
        # If no code in URL, show input field
        if not code:
            code = st.text_input("Enter the code from the redirect URL:")
        
        if code:
            st.write("Debug: Attempting to exchange code for token")
            token_response = requests.post(
                STRAVA_TOKEN_URL,
                data={
                    'client_id': STRAVA_CLIENT_ID,
                    'client_secret': STRAVA_CLIENT_SECRET,
                    'code': code,
                    'grant_type': 'authorization_code'
                },
                verify=False
            )
            if token_response.ok:
                st.session_state.strava_token = token_response.json()['access_token']
                # Clear URL parameters
                st.experimental_set_query_params()
                st.rerun()
            else:
                st.error(f"Authentication failed: {token_response.text}")
                st.write("Debug: Token exchange response:", token_response.text)
    except Exception as e:
        st.error(f"Error during authentication: {str(e)}")
# Add back the CSS
st.markdown("""
    <style>
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    .header-container h1 {
        margin: 0;
        white-space: nowrap;
    }
    .monthly-summary {
        display: flex;
        gap: 20px;
        background-color: white;
        padding: 12px;
        border-radius: 4px;
        font-size: 1.1em;
    }
    .month-metric {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .calendar-container {
        display: flex;
        align-items: start;
    }
    .week-numbers {
        display: grid;
        margin-right: 8px;
        margin-top: 52px;
        background-color: white;
    }
    .week-number {
        height: 150px;
        width: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
        font-size: 0.85em;
        padding: 0;
        text-align: center;
    }
    .main-calendar {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .calendar-content {
        display: flex;
        align-items: start;
    }
    .calendar-grid {
        flex-grow: 1;
        border: 1px solid #ddd;
        border-radius: 4px;
        overflow: hidden;
    }
    .calendar-header {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        background-color: #f8f9fa;
        border-bottom: 1px solid #ddd;
        height: 44px;
        align-items: center;
    }
    .summary-column {
        width: 200px;
        margin-left: 8px;
        margin-top: 44px;
    }
    .calendar-week {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        height: 150px;
    }
    .calendar-day {
        padding: 12px;
        border-right: 1px solid #ddd;
        border-bottom: 1px solid #ddd;
        height: 150px;
        overflow-y: auto;
        background-color: white;
    }
    .adjacent-day {
        background-color: #f8f9fa;
    }
    .adjacent-day .day-number {
        color: #999;
    }
    .day-number {
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 1.1em;
    }
    .activity {
        font-size: 0.9em;
        margin: 4px 0;
        padding: 4px 8px;
        border-radius: 3px;
    }
    .weekly-summary {
        height: 150px;
        padding: 12px;
        background-color: white;
        border: none;
        font-size: 0.9em;
        margin-bottom: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .summary-metric {
        margin: 4px 0;
    }
    </style>
""", unsafe_allow_html=True)

