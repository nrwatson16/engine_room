import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import pytz
from dotenv import load_dotenv
import os
import urllib3
import calendar
from calendar import monthcalendar, month_name
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_base_url():
    return "https://trainingcal.streamlit.app"

# Load environment variables
load_dotenv()

# Strava API settings
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"

# Get user's timezone
CENTRAL_TZ = pytz.timezone('America/Chicago')
UTC = pytz.UTC

# Configure page for better mobile/tablet viewing
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed on iPad
)

# Updated CSS with iPad optimizations
st.markdown("""
    <style>
    /* Main container styles */
    .main > div:first-child {
        padding: 1rem !important;
    }
    
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 24px;
        padding: 0 8px;
    }

    .header-container h1 {
        margin: 0;
        font-size: 1.75em;
    }

    .monthly-summary {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        background-color: white;
        padding: 16px;
        border-radius: 8px;
        font-size: 1.2em;
        width: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .month-metric {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background-color: #f8f9fa;
        border-radius: 6px;
        min-width: 120px;
    }

    .calendar-container {
        display: flex;
        align-items: start;
        padding: 0 8px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }

    .week-numbers {
        display: none;
    }

    .main-calendar {
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    .calendar-content {
        display: flex;
        align-items: start;
        width: 100%;
    }

    .calendar-grid {
        flex-grow: 1;
        border: 1px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .calendar-header {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        background-color: #f8f9fa;
        border-bottom: 1px solid #ddd;
        height: 50px;
        align-items: center;
        font-size: 1.1em;
        position: sticky;
        top: 0;
        z-index: 1;
    }

    .summary-column {
        width: 180px;
        margin-left: 12px;
        background-color: #f8f9fa;
        border-radius: 8px;
        overflow: hidden;
    }

    .calendar-week {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        min-height: 180px;
    }

    .calendar-day {
        padding: 12px;
        border-right: 1px solid #ddd;
        border-bottom: 1px solid #ddd;
        min-height: 180px;
        overflow-y: auto;
        background-color: white;
        touch-action: pan-y pinch-zoom;
    }

    .adjacent-day {
        background-color: #f8f9fa;
    }

    .adjacent-day .day-number {
        color: #999;
    }

    .day-number {
        font-weight: bold;
        margin-bottom: 12px;
        font-size: 1.2em;
        color: #333;
    }

    .activity {
        font-size: 1em;
        margin: 8px 0;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: #f8f9fa;
        border: 1px solid #eee;
        touch-action: pan-y;
    }

    .weekly-summary {
        height: 180px;
        padding: 16px;
        background-color: white;
        border: none;
        font-size: 1em;
        margin-bottom: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .summary-metric {
        margin: 4px 0;
        padding: 8px;
        background-color: #f8f9fa;
        border-radius: 6px;
    }

    /* iPad-specific media queries */
    @media (max-width: 1024px) {
        .calendar-container {
            flex-direction: column;
        }
        
        .summary-column {
            width: 100%;
            margin-left: 0;
            margin-top: 16px;
        }
        
        .weekly-summary {
            height: auto;
            padding: 12px;
            flex-direction: row;
            flex-wrap: wrap;
            justify-content: space-around;
        }
        
        .summary-metric {
            flex: 1;
            min-width: 150px;
            text-align: center;
        }
        
        .calendar-day {
            min-height: 150px;
        }
    }

    /* Touch-friendly styles */
    * {
        -webkit-tap-highlight-color: rgba(0,0,0,0);
    }

    .activity:active {
        background-color: #e9ecef;
    }

    /* Improve scrolling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    /* Streamlit-specific overrides for better iPad display */
    .stSelectbox {
        min-width: 200px;
    }

    .stButton button {
        width: 100%;
        padding: 0.75rem !important;
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

def calculate_weekly_stats(activities_df, start_date, end_date):
    """Calculate weekly statistics for the given date range."""
    week_activities = activities_df[
        (activities_df['date'] >= start_date) & 
        (activities_df['date'] <= end_date)
    ]
    
    # Calculate cycling stats
    cycling = week_activities[week_activities['type'] == 'Ride']
    total_miles = cycling['distance_miles'].sum()
    avg_power = cycling['average_watts'].mean() if 'average_watts' in cycling.columns else None
    
    # Calculate total relative effort (suffer score)
    total_effort = week_activities['suffer_score'].sum() if 'suffer_score' in week_activities.columns else None
    
    return {
        'miles': f"{total_miles:.1f}" if not pd.isna(total_miles) else "0",
        'power': f"{avg_power:.0f}" if avg_power and not pd.isna(avg_power) else "-",
        'effort': f"{total_effort:.0f}" if total_effort and not pd.isna(total_effort) else "-"
    }

def calculate_monthly_stats(activities_df, year, month):
    """Calculate monthly statistics."""
    month_activities = activities_df[
        (activities_df['start_date'].dt.year == year) & 
        (activities_df['start_date'].dt.month == month)
    ]
    
    # Calculate cycling stats
    cycling = month_activities[month_activities['type'] == 'Ride']
    total_miles = cycling['distance_miles'].sum()
    avg_power = cycling['average_watts'].mean() if 'average_watts' in cycling.columns else None
    
    # Calculate total relative effort (suffer score)
    total_effort = month_activities['suffer_score'].sum() if 'suffer_score' in month_activities.columns else None
    
    return {
        'miles': f"{total_miles:.1f}" if not pd.isna(total_miles) else "0",
        'power': f"{avg_power:.0f}" if avg_power and not pd.isna(avg_power) else "-",
        'effort': f"{total_effort:.0f}" if total_effort and not pd.isna(total_effort) else "-"
    }

# Strava authentication
if 'strava_token' not in st.session_state:
    try:
        base_url = get_base_url()
        auth_link = f"{STRAVA_AUTH_URL}?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={base_url}&scope=read,activity:read_all,profile:read_all"
        st.markdown(f"[Connect to Strava]({auth_link})")
        
        # Get the code from URL params if present
        query_params = st.experimental_get_query_params()
        code = query_params.get("code", [None])[0]
        
        # If no code in URL, show input field
        if not code:
            code = st.text_input("Enter the code from the redirect URL:")
        
        if code:
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
                st.markdown("Please try connecting to Strava again.")
    except Exception as e:
        st.error(f"Error during authentication: {str(e)}")
        st.markdown("Please try connecting to Strava again.")
# Main app
if 'strava_token' in st.session_state:
    
    try:
        # Set time boundaries
        after_date = datetime(2024, 1, 1)  # Start of 2024
        after_timestamp = int(after_date.timestamp())
        before_timestamp = int(datetime.now().timestamp())
        
        # Initialize empty list for all activities
        all_activities = []
        page = 1
        
        while True:
            response = requests.get(
                "https://www.strava.com/api/v3/athlete/activities",
                headers={'Authorization': f"Bearer {st.session_state.strava_token}"},
                params={
                    'after': after_timestamp,
                    'before': before_timestamp,
                    'per_page': 200,
                    'page': page
                },
                verify=False
            )
            
            if not response.ok:
                st.error(f"Failed to fetch activities: {response.text}")
                break
                
            page_activities = response.json()
            if not page_activities:
                break
                
            all_activities.extend(page_activities)
            page += 1
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching activities: {str(e)}")
        
    if all_activities:
        df = pd.DataFrame(all_activities)
        
        df = pd.DataFrame(all_activities)
    
        # Convert distance to miles first
        df['distance_miles'] = df['distance'] / 1609.34
    
        # Convert timestamps to datetime objects
        df['start_date'] = pd.to_datetime(df['start_date'])

        # Convert to Central time and extract date
        df['start_date'] = df['start_date'].apply(
        lambda x: x.tz_localize(UTC) if x.tzinfo is None else x
        ).dt.tz_convert(CENTRAL_TZ)

        # Extract date in Central time based on the local time of activity
        df['date'] = df.apply(lambda row: 
        # If activity starts before 3am local time, consider it part of previous day
        (row['start_date'] - timedelta(days=1)).date() 
        if row['start_date'].hour < 3 
        else row['start_date'].date(), 
        axis=1)
    
        # Group activities by date
        activities_by_date = df.groupby('date').apply(
            lambda x: pd.Series({
                'activities': sorted([
                    {
                        'name': row['name'],
                        'type': row['type'],
                        'distance': f"{row['distance_miles']:.1f}",
                        'watts': f"{row['average_watts']:.0f}" if 'average_watts' in row and pd.notnull(row['average_watts']) else None,
                        'start_time': row['start_date']  # Include start time for sorting
                    }
                    for _, row in x.iterrows()
                ], key=lambda x: x['start_time'])  # Sort by start time
            })
        ).to_dict()['activities']
        
        # Year selector
        current_year = datetime.now().year
        years = list(range(current_year, 2023, -1))  # Creates descending list from current_year down to 2024
        selected_year = st.sidebar.selectbox(
            "Select Year",
            years,
            index=0  # Default to current year (first in list now)
        )

        # Month selector
        current_month = datetime.now().month
        
        # If selected year is current year, only show months up to current month
        if selected_year == current_year:
            months = list(range(current_month, 0, -1))
        else:
            # For past years, show all months
            months = list(range(12, 0, -1))
            
        month_names = {i: calendar.month_name[i] for i in months}
        selected_month_num = st.sidebar.selectbox(
            "Select Month",
            months,
            format_func=lambda x: month_names[x],
            index=0  # Default to most recent month
        )

        # Create selected_month datetime object for use in rest of the code
        selected_month = datetime(selected_year, selected_month_num, 1)

        # Calculate monthly stats
        monthly_stats = calculate_monthly_stats(df, selected_month.year, selected_month.month)

        # Display header with monthly stats
        st.markdown(f'''
            <div class="header-container">
                <h1>{month_name[selected_month.month]} {selected_month.year}</h1>
                <div class="monthly-summary">
                    <div class="month-metric">🚲 {monthly_stats['miles']} mi</div>
                    <div class="month-metric">⚡ {monthly_stats['power']}W</div>
                    <div class="month-metric">🔥 {monthly_stats['effort']}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Create calendar
        cal = monthcalendar(selected_month.year, selected_month.month)
        
        calendar_html = ['<div class="calendar-container">']
        
        # Week numbers column
        calendar_html.append('<div class="week-numbers">')
        for week in cal:
            if any(week):
                valid_days = [day for day in week if day != 0]
                if valid_days:
                    try:
                        sample_date = datetime(selected_month.year, selected_month.month, valid_days[0])
                        monday_date = sample_date - timedelta(days=sample_date.weekday())
                        week_num = monday_date.isocalendar()[1]
                        calendar_html.append(f'<div class="week-number">W{week_num}</div>')
                    except ValueError:
                        calendar_html.append('<div class="week-number">-</div>')
        calendar_html.append('</div>')
        
        # Calendar content
        calendar_html.append('<div class="calendar-content">')
        
        # Main calendar grid
        calendar_html.append('<div class="calendar-grid">')
        
        # Header row
        calendar_html.append('<div class="calendar-header">')
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            calendar_html.append(f'<div class="calendar-day">{day}</div>')
        calendar_html.append('</div>')
        
        # Calendar days
        for week in cal:
            calendar_html.append('<div class="calendar-week">')
            for day in week:
                if day == 0:
                    calendar_html.append('<div class="calendar-day adjacent-day"></div>')
                else:
                    date = datetime(selected_month.year, selected_month.month, day).date()
                    calendar_html.append(f'<div class="calendar-day">')
                    calendar_html.append(f'<div class="day-number">{day}</div>')
                    
                    if date in activities_by_date:
                        for activity in activities_by_date[date]:
                            activity_str = ""
                            if activity['type'] == 'Ride':
                                activity_str = f"🚲 {activity['distance']}mi"
                                if activity['watts']:
                                    activity_str += f" ({activity['watts']}W)"
                            elif activity['type'] == 'Yoga':
                                activity_str = f"🧘‍♀️ {activity['name']}"
                            else:
                                activity_str = f"💪 {activity['name']}"
                            
                            # Optionally, you can also display the time
                            # time_str = activity['start_time'].strftime('%I:%M %p')
                            # activity_str = f"{time_str} - {activity_str}"
                            
                            calendar_html.append(f'<div class="activity">{activity_str}</div>')
                    calendar_html.append('</div>')
            calendar_html.append('</div>')
        
        calendar_html.append('</div>')  # Close calendar grid
        
        # Summary column
        calendar_html.append('<div class="summary-column">')
        for week in cal:
            if any(week):
                # Find start and end dates for the week
                valid_days = [day for day in week if day != 0]
                if valid_days:
                    week_start_date = datetime(selected_month.year, selected_month.month, valid_days[0]).date()
                    week_end_date = datetime(selected_month.year, selected_month.month, valid_days[-1]).date()
                    
                    weekly_stats = calculate_weekly_stats(df, week_start_date, week_end_date)
                    calendar_html.append(f'<div class="weekly-summary">')
                    calendar_html.append(f'<div class="summary-metric">🚲 {weekly_stats["miles"]} miles</div>')
                    calendar_html.append(f'<div class="summary-metric">⚡ {weekly_stats["power"]}W avg</div>')
                    calendar_html.append(f'<div class="summary-metric">🔥 {weekly_stats["effort"]} effort</div>')
                    calendar_html.append('</div>')
        
        calendar_html.append('</div>')  # Close summary column
        calendar_html.append('</div>')  # Close calendar content
        calendar_html.append('</div>')  # Close calendar container
        
        # Display the calendar
        st.markdown(''.join(calendar_html), unsafe_allow_html=True)
    else:
        st.error(f"Failed to fetch activities: {response.text}")
