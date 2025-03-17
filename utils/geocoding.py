import streamlit as st

# Function to geocode location
def geocode_location(location_name, gmaps):
    """Convert location name to coordinates"""
    try:
        geocode_result = gmaps.geocode(location_name)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location
        return None
    except Exception as e:
        st.error(f"Error geocoding location: {str(e)}")
        return None