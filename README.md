# Smart Travel Agent

## Overview
A comprehensive travel recommendation application that leverages LLMs (Large Language Models) and the Google Maps API to create personalized travel experiences. Built using Streamlit.

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

### AI and Language Models
- **LangChain:** Framework for developing applications powered by language models
- **LLM:** Integration with OpenAI's GPT-3.5 Turbo model for generating intelligent travel recommendations
- **LLMChain:** For creating structured recommendation chains with prompt templates
- **PromptTemplates:** Custom-designed prompts for travel recommendation generation
- **JSON Structured Output**

### APIs and Data Sources
- **Google Maps Platform**: Core location data source with multiple endpoints:
- Places API for discovering points of interest
- Geocoding API for converting location names to coordinates
- Place Details API for comprehensive place information
- Place Photos API for visual content

### Frontend and Visualization
- **Streamlit**
- **Folium**
- **Streamlit-Folium**
- **Pandas**

### Other Technologies
- **Python**
- **dotenv - Environment Variable Management**
- **JSON**

## 🚀 How It Works

1. **User Input:** Users enter their destination, travel dates, and preferences.
2. **Geocoding:** The application converts the location name to coordinates.
3. **LLM call:** Places data is processed through LangChain and the LLM Model (GPT-3.5 Turbo).
4. **Intelligent Filtering:** Results are filtered based on travel style and other preferences.
5. **Visualization:** Recommendations are displayed in an intuitive card layout and interactive map.

## 🛠️ Setup and Installation

1. **Clone this repository**: <br>
git clone https://github.com/yourusername/smart-travel-agent.git <br>
cd smart-travel-agent

2. **Install the required packages:**
   
3. **Provide API Keys** : <br>
OPENAI_API_KEY=your_openai_api_key <br>
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

4. **Run the Streamlit application:**
   streamlit run app.py
