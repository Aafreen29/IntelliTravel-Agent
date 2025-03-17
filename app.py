import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType, Tool, initialize_agent
import googlemaps
import json
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Import utility modules
from utils.geocoding import geocode_location
from utils.places import (
    get_recommendations, 
    generate_simple_descriptions,
    get_destination_image,
    CATEGORY_MAPPING
)
from utils.mapping import display_recommendation_map
from utils.display import display_recommendation_cards

# Load environment variables
load_dotenv()

# Initialize API clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)

# Set up Streamlit UI
st.set_page_config(page_title="IntelliTravel Agent", layout="wide")

# Set a static background color for the sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #e6f3ff;  /* Light gray color - change to your preferred color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("IntelliTravel Agent")
st.subheader("Discover the best places to visit, eat, and enjoy")

# Initialize session state variables
if 'location' not in st.session_state:
    st.session_state.location = ""
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = {}
if 'current_category' not in st.session_state:
    st.session_state.current_category = None
if 'travel_style' not in st.session_state:
    st.session_state.travel_style = "Any"
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date()
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.now().date()
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Create sidebar for location input and preferences
with st.sidebar:
    st.header("Plan Your Trip")
    
    # Add a div with a class for better readability when background is active
    form_container_class = "sidebar-bg-active" if st.session_state.form_submitted else ""
    
    # Create a form for all inputs
    with st.form("trip_form", clear_on_submit=False):
        # # You can wrap this part in a div with the class if needed
        # if st.session_state.form_submitted:
        #     st.markdown(f'<div class="{form_container_class}">', unsafe_allow_html=True)
        
        location_input = st.text_input("Enter your destination:", 
                                      placeholder="e.g., Paris, France")
        
        st.subheader("When are you visiting?")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", datetime.now().date())
        with col2:
            end_date = st.date_input("To", datetime.now().date())
        
        # Add travel preferences
        st.subheader("Travel Preferences")
        
        travel_style = st.selectbox(
            "Travel Style",
            options=["Any", "Budget", "Mid-range", "Luxury"]
        )

        if st.session_state.form_submitted:
            st.markdown('</div>', unsafe_allow_html=True)

        # Submit button
        submitted = st.form_submit_button("Find Recommendations", use_container_width=True)
        
        if submitted:
            # Update session state
            if location_input:
                with st.spinner("Finding your destination..."):
                    st.session_state.location = location_input
                    
                    # Get coordinates
                    coordinates = geocode_location(location_input, gmaps)
                    if coordinates and 'lat' in coordinates and 'lng' in coordinates:
                        st.session_state.coordinates = coordinates
                        st.session_state.start_date = start_date
                        st.session_state.end_date = end_date
                        st.session_state.travel_style = travel_style
                        st.session_state.form_submitted = True
                        
                        # Reset recommendations when form is submitted with new data
                        st.session_state.recommendations = {}
                        st.session_state.current_category = None

                        # Success message
                        st.success(f"Ready to explore {location_input}!")
                    else:
                        st.error("Could not find the specified location. Please try again.")
                        st.session_state.coordinates = None
                        st.session_state.form_submitted = False
            else:
                st.error("Please enter a destination.")
                
    # Show trip details after submission
    if st.session_state.form_submitted and st.session_state.location:
        st.write(f"**Destination:** {st.session_state.location}")
        st.write(f"**Dates:** {st.session_state.start_date.strftime('%b %d')} - {st.session_state.end_date.strftime('%b %d, %Y')}")
        st.write(f"**Travel Style:** {st.session_state.travel_style}")
        
        # Trip duration
        trip_days = (st.session_state.end_date - st.session_state.start_date).days + 1
        st.write(f"**Trip Duration:** {trip_days} {'day' if trip_days == 1 else 'days'}")

# Main content area - only show if form submitted
if st.session_state.form_submitted and st.session_state.location and st.session_state.coordinates:
    # Category navigation
    categories = ["Food", "Attractions", "Activities", "Shopping", "Nightlife", "Nature"]
    category_icons = ["🍽️", "🏛️", "🎯", "🛍️", "🌃", "🌳"]
    
    # Create category buttons
    cat_cols = st.columns(len(categories))
    
    for i, (category, icon) in enumerate(zip(categories, category_icons)):
        if cat_cols[i].button(f"{icon} {category}", use_container_width=True):
            st.session_state.current_category = category.lower()
            
            # Check if we already have recommendations for this category with current travel style
            cache_key = f"{category.lower()}_{st.session_state.travel_style}"
            if cache_key not in st.session_state.recommendations:
                with st.spinner(f"Finding the best {category.lower()} recommendations for {st.session_state.travel_style} travelers..."):
                    # Get recommendations with travel style
                    recommendations = get_recommendations(
                        category.lower(), 
                        st.session_state.location,
                        st.session_state.coordinates,
                        gmaps,
                        llm,
                        st.session_state.travel_style
                    )
                    
                    # If recommendations don't have descriptions, generate simple ones
                    if recommendations and not any(p.get('description') for p in recommendations):
                        recommendations = generate_simple_descriptions(
                            recommendations,
                            category.lower(),
                            st.session_state.location,
                            st.session_state.travel_style
                        )
                    
                    st.session_state.recommendations[cache_key] = recommendations
    
    # Display recommendations for the selected category
    if st.session_state.current_category:
        category = st.session_state.current_category
        cache_key = f"{category}_{st.session_state.travel_style}"
        
        # Display header with travel style information
        style_text = f" for {st.session_state.travel_style} Travelers" if st.session_state.travel_style != "Any" else ""
        st.header(f"Top {category.title()} in {st.session_state.location}{style_text}")
        
        # Check if we have recommendations
        if cache_key in st.session_state.recommendations and st.session_state.recommendations[cache_key]:
            # Create tabs for different views
            tab1, tab2 = st.tabs(["Recommendations", "Map View"])
            
            with tab1:
                # Display recommendations in a card layout
                display_recommendation_cards(st.session_state.recommendations[cache_key], category)
            
            with tab2:
                # Display map
                display_recommendation_map(
                    st.session_state.recommendations[cache_key],
                    st.session_state.location,
                    st.session_state.coordinates
                )
        else:
            if cache_key not in st.session_state.recommendations:
                with st.spinner(f"Finding the best {category} recommendations for {st.session_state.travel_style} travelers..."):
                    # Get recommendations with travel style
                    recommendations = get_recommendations(
                        category, 
                        st.session_state.location,
                        st.session_state.coordinates,
                        gmaps,
                        llm,
                        st.session_state.travel_style
                    )
                    
                    # If recommendations don't have descriptions, generate simple ones
                    if recommendations and not any(p.get('description') for p in recommendations):
                        recommendations = generate_simple_descriptions(
                            recommendations,
                            category,
                            st.session_state.location,
                            st.session_state.travel_style
                        )
                    
                    st.session_state.recommendations[cache_key] = recommendations
                
                # Check if we found any recommendations
                if st.session_state.recommendations[cache_key]:
                    # Rerun to display the recommendations
                    st.rerun()
                else:
                    st.info(f"No {category} recommendations found for {st.session_state.location} with {st.session_state.travel_style} travel style.")
            else:
                st.info(f"No {category} recommendations found for {st.session_state.location} with {st.session_state.travel_style} travel style.")
else:
    # Welcome message when no form submitted
    st.info("👈 Enter your travel details in the sidebar and click 'Find Recommendations' to get started!")
    
    st.write("""
    
    This application helps you discover the best places to visit, eat, and enjoy during your travels.
    Simply enter your destination, travel dates, and preferences in the sidebar form to get started.
    
    ### Features:
    - Find top-rated restaurants and food options
    - Discover popular tourist attractions
    - Explore exciting activities to do
    - Find shopping destinations
    - Check out nightlife options
    - Find nature spots and parks
    - Personalize recommendations based on your travel style
    - View all recommendations on an interactive map
    
    ### How to use:
    1. Enter your destination in the sidebar
    2. Select your travel dates
    3. Choose your travel style (Budget, Mid-range, or Luxury)
    4. Click "Find Recommendations"
    5. Browse different categories using the buttons above
    
    Start planning your perfect trip today!
    """)