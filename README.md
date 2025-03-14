# Smart Travel Agent

## Overview
A comprehensive travel recommendation application that leverages LLMs (Large Language Models) and the Google Maps API to create personalized travel experiences. Its built with Streamlit.

## 🌟 Features

- **Destination-Based Recommendations**
  - 🍽️ Food & Restaurants
  - 🏛️ Tourist Attractions
  - 🎯 Activities & Entertainment
  - 🛍️ Shopping Destinations
  - 🌃 Nightlife Options
  - 🌳 Nature & Outdoor Spots

- **Preference-Based Filtering**
  - Budget-friendly options
  - Mid-range experiences
  - Luxury destinations

- **Interactive Map View**
  - Color-coded markers based on ratings
  - Detailed pop-ups with place information
  - Visual representation of search radius

- **Rich Information Display**
  - Rating and review count
  - Price level indicators
  - Current open/closed status
  - LLM-generated personalized descriptions
  - Curated highlights
  - Direct links to websites and Google Maps

- **Trip Planning Tools**
  - Date range selection
  - Trip duration calculation
  - Travel style preferences

## 🧠 Technology Stack

### LLM Integration
- **LangChain Framework**
- **ChatOpenAI**
- **LLMChain with PromptTemplates**
- **Natural Language Generation**
- **JSON Structured Output**

### APIs and Data Sources
- **Google Maps Platform**
  - Places API 
  - Geocoding API
  - Photos API

### Frontend and Visualization
- **Streamlit**
- **Folium**
- **Streamlit-Folium**
- **Pandas**

### Other Technologies
- **Python**
- **Environment Variable Management**
- **Dynamic UI Components**
- **Session State Management**

## 🚀 How It Works

1. **Intelligent Category Mapping**
2. **Enhanced Place Search**
   - Place types specific to each category
   - Travel style preferences
   - Keyword expansion for comprehensive results
   - Price level filtering based on travel style
   - Rating and popularity-based sorting

3. **LLM Enhancement Pipeline**
   - Processes raw place data into a structured format
   - Sends simplified place information to the LLM
   - Generates personalized descriptions and highlights
   - Integrates enhanced content back with original place data
   - Provides fallback description generation if LLM processing fails

4. **User Interface Flow**
   - Location input and preference selection in sidebar
   - Category navigation through icon buttons
   - Tabbed interface for switching between list and map views
   - Card-based presentation of recommendations
   - Interactive map with detailed markers

## 🛠️ Setup and Installation

1. Clone this repository
2. Install the required packages:
