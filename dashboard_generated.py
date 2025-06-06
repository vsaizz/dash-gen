import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

# Function to get start and end dates of current week (Monday to Sunday)
def get_current_week_dates():
    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')

# Fetch data from NASA APIs
@st.cache
def fetch_nasa_data():
    api_key = 'DEMO_KEY'
    start_date_str, end_date_str = get_current_week_dates()

    # Solar Flares
    flr_url = f'https://api.nasa.gov/DONKI/FLR?startDate={start_date_str}&endDate={end_date_str}&api_key={api_key}'
    try:
        solar_flares_response = requests.get(flr_url)
        solar_flares = solar_flares_response.json()
        if not isinstance(solar_flares, list):
            solar_flares = []
    except Exception:
        solar_flares = []

    # Notifications for Sunspots
    notifications_url = f'https://api.nasa.gov/DONKI/notifications?startDate={start_date_str}&endDate={end_date_str}&type=all&api_key={api_key}'
    try:
        notifications_response = requests.get(notifications_url)
        notifications = notifications_response.json()
        if not isinstance(notifications, list):
            notifications = []
    except Exception:
        notifications = []

    # Filter Sunspot Events
    sunspot_events = [
        event for event in notifications
        if 'sunspot' in event.get('messageType', '').lower() or 'sunspot' in event.get('messageBody', '').lower()
    ]

    # CMEs
    cme_url = f'https://api.nasa.gov/DONKI/CME?startDate={start_date_str}&endDate={end_date_str}&api_key={api_key}'
    try:
        cme_response = requests.get(cme_url)
        cmes = cme_response.json()
        if not isinstance(cmes, list):
            cmes = []
    except Exception:
        cmes = []

    return solar_flares, sunspot_events, cmes

# Process data into DataFrames for visualization
def process_data(solar_flares, sunspot_events, cmes):
    # Solar Flares DataFrame
    flare_df = pd.DataFrame(solar_flares)
    if not flare_df.empty:
        flare_df['date'] = pd.to_datetime(flare_df['beginTime'])
    else:
        flare_df['date'] = pd.to_datetime([])

    # CMEs DataFrame
    cme_df = pd.DataFrame(cmes)
    if not cme_df.empty:
        cme_df['date'] = pd.to_datetime(cme_df['launchDate'])
    else:
        cme_df['date'] = pd.to_datetime([])

    # Sunspot Events DataFrame
    # Assuming messageBody contains info like 'Sunspot number: X'
    sunspot_list = []
    for event in sunspot_events:
        message = event.get('messageBody', '')
        date_str = event.get('publishDate', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%MZ')
        except:
            date_obj = None
        # Extract sunspot number if possible
        sunspot_number = None
        if 'sunspot' in message.lower():
            import re
            match = re.search(r'sunspot.*?(\d+)', message.lower())
            if match:
                sunspot_number = int(match.group(1))
        sunspot_list.append({
            'date': date_obj,
            'message': message,
            'sunspot_number': sunspot_number
        })
    sunspot_df = pd.DataFrame(sunspot_list)
    return flare_df, sunspot_df, cme_df

# Main app
def main():
    st.title("Solar Events This Week")
    st.write("An interactive dashboard displaying all solar events that occurred during the current week, including solar flares, sunspots, and coronal mass ejections.")

    # Fetch data
    with st.spinner("Loading data from NASA APIs..."):
        solar_flares, sunspot_events, cmes = fetch_nasa_data()

    # Process data
    flare_df, sunspot_df, cme_df = process_data(solar_flares, sunspot_events, cmes)

    # Summary statistics
    st.header("Key Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Solar Flares", len(flare_df))
    col2.metric("Sunspot Events", len(sunspot_df))
    col3.metric("CMEs", len(cme_df))

    # Filters
    st.sidebar.header("Filters")
    # Date range filter
    start_date, end_date = get_current_week_dates()
    date_range = st.sidebar.date_input("Select Date Range", [datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')])
    if len(date_range) == 2:
        start_filter, end_filter = date_range
    else:
        start_filter, end_filter = date_range[0], date_range[0]
    # Event type filter
    event_type = st.sidebar.selectbox("Event Type", ["All", "Solar Flares", "Sunspots", "CMEs"])

    # Filter data based on user input
    def filter_df(df, date_col):
        if df.empty:
            return df
        mask = (df[date_col] >= pd.to_datetime(start_filter)) & (df[date_col] <= pd.to_datetime(end_filter))
        return df[mask]

    filtered_flare_df = filter_df(flare_df, 'date')
    filtered_sunspot_df = filter_df(sunspot_df, 'date')
    filtered_cme_df = filter_df(cme_df, 'date')

    # Visualization
    st.header("Solar Flares and CMEs Timeline")
    timeline_df = pd.concat([
        filtered_flare_df.assign(EventType='Solar Flare'),
        filtered_cme_df.assign(EventType='CME')
    ])
    if not timeline_df.empty:
        fig = px.scatter(
            timeline_df,
            x='date',
            y='EventType',
            hover_data=['message'],
            title='Solar Flares and CMEs over the Week',
            labels={'date': 'Date', 'EventType': 'Event Type'}
        )
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No solar flare or CME data available for the selected filters.")

    st.header("Sunspot Activity")
    if not sunspot_df.empty:
        # Filter by sunspot number if desired
        min_sunspot = st.slider("Minimum Sunspot Number", min_value=0, max_value=int(sunspot_df['sunspot_number'].max() or 0))
        filtered_sunspot_df = sunspot_df[sunspot_df['sunspot_number'] >= min_sunspot]
        daily_counts = filtered_sunspot_df.groupby(filtered_sunspot_df['date'].dt.date).size().reset_index(name='Count')
        fig2 = px.bar(
            daily_counts,
            x='date',
            y='Count',
            labels={'date': 'Date', 'Count': 'Number of Sunspots'},
            title='Daily Sunspot Counts'
        )
        st.plotly_chart(fig2, use_container_width=True)
        # Show detailed list
        st.subheader("Sunspot Events Details")
        st.dataframe(filtered_sunspot_df[['date', 'message', 'sunspot_number']])
    else:
        st.write("No sunspot data available for the selected filters.")

    st.header("Notable Events")
    # List of events
    if not filtered_flare_df.empty:
        st.subheader("Solar Flares")
        st.dataframe(filtered_flare_df[['date', 'message']])
    if not filtered_cme_df.empty:
        st.subheader("Coronal Mass Ejections")
        st.dataframe(filtered_cme_df[['date']])
    if not filtered_sunspot_df.empty:
        st.subheader("Sunspot Events")
        st.dataframe(filtered_sunspot_df[['date', 'message', 'sunspot_number']])

    # Export options
    st.sidebar.header("Export Data")
    if st.sidebar.button("Download All Data as CSV"):
        combined_df = pd.concat([
            flare_df.assign(EventType='Solar Flare'),
            cme_df.assign(EventType='CME'),
            sunspot_df.assign(EventType='Sunspot')
        ])
        combined_df['date'] = combined_df['date'].astype(str)
        csv = combined_df.to_csv(index=False).encode()
        st.sidebar.download_button("Download CSV", data=csv, file_name="solar_events_week.csv", mime="text/csv")

if __name__ == "__main__":
    main()