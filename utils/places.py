import streamlit as st
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Create category mapping for proper search types
CATEGORY_MAPPING = {
    "food": {
        "types": ["restaurant", "cafe", "bakery", "bar", "meal_takeaway", "meal_delivery"],
        "keywords": ["food", "dining", "restaurants", "eat", "cuisine"]
    },
    "attractions": {
        "types": ["tourist_attraction", "museum", "art_gallery", "aquarium", "zoo", "landmark"],
        "keywords": ["sightseeing", "landmark", "tourist", "attractions", "visit"] 
    },
    "activities": {
        "types": ["amusement_park", "movie_theater", "bowling_alley", "stadium", "park", "spa", 
                 "gym", "shopping_mall", "night_club", "casino"],
        "keywords": ["activity", "fun", "entertainment", "experience", "adventure"]
    },
    "shopping": {
        "types": ["shopping_mall", "department_store", "clothing_store", "electronics_store", "jewelry_store"],
        "keywords": ["shopping", "store", "mall", "buy", "shop"]
    },
    "nightlife": {
        "types": ["night_club", "bar", "movie_theater", "casino"],
        "keywords": ["nightlife", "night", "club", "entertainment", "evening"]
    },
    "nature": {
        "types": ["park", "campground", "natural_feature", "beach"],
        "keywords": ["nature", "outdoor", "park", "hiking", "beach"]
    }
}

# Enhanced place search with category intelligence and travel style filtering
def enhanced_place_search(category, location_coords, location_name, gmaps, travel_style="Any", radius=5000, limit=15):
    """
    Perform an enhanced search for places using category intelligence and travel style preference
    """
    all_results = []
    
    # Get category information
    if category.lower() in CATEGORY_MAPPING:
        category_info = CATEGORY_MAPPING[category.lower()]
        search_types = category_info["types"]
        keywords = category_info["keywords"]
    else:
        # Default to generic search if category not found
        search_types = [category.lower()]
        keywords = [category.lower()]
    
    # Search by each type in the category
    for place_type in search_types:
        try:
            # Adjust query based on travel style
            style_keyword = ""
            if travel_style != "Any":
                style_keyword = f"{travel_style.lower()} "
            
            # Basic place search by type with style preference
            result = gmaps.places(
                query=f"{style_keyword}{place_type} in {location_name}",
                location=location_coords,
                radius=radius,
                type=place_type
            )
            
            if 'results' in result and result['results']:
                for place in result['results']:
                    place['search_type'] = place_type
                    all_results.append(place)
                    
            # If we need more results, try using keywords
            if len(all_results) < 5 and keywords:
                for keyword in keywords:
                    keyword_result = gmaps.places(
                        query=f"{style_keyword}{keyword} in {location_name}",
                        location=location_coords,
                        radius=radius
                    )
                    
                    if 'results' in keyword_result and keyword_result['results']:
                        for place in keyword_result['results']:
                            place['search_type'] = f"{keyword} search"
                            all_results.append(place)
        except Exception as e:
            st.error(f"Error searching for {place_type}: {str(e)}")
            continue
    
    # Deduplicate results by place_id
    unique_places = {}
    for place in all_results:
        if place['place_id'] not in unique_places:
            unique_places[place['place_id']] = place
    
    # Get place details for top results for more comprehensive data
    detailed_places = []
    
    # Filter based on price level for travel style if applicable
    filtered_places = unique_places.values()
    if travel_style != "Any":
        price_ranges = {
            "Budget": [0, 1],
            "Mid-range": [1, 2],
            "Luxury": [2, 3, 4]
        }
        
        if travel_style in price_ranges:
            # Filter places by price level when available
            price_filtered = []
            no_price_info = []
            
            for place in filtered_places:
                if 'price_level' in place:
                    if place['price_level'] in price_ranges[travel_style]:
                        price_filtered.append(place)
                else:
                    # Keep places without price info as fallbacks
                    no_price_info.append(place)
            
            # Use price-filtered places first, then add others if needed
            if price_filtered:
                filtered_places = price_filtered
            elif not price_filtered and not no_price_info:
                # If filtering removed all results, fall back to original list
                filtered_places = unique_places.values()
    
    # Sort by prominence and rating
    sorted_places = sorted(
        filtered_places,
        key=lambda x: (x.get('rating', 0) * x.get('user_ratings_total', 1)/100),
        reverse=True
    )
    
    # Get details for top places
    top_places = sorted_places[:min(limit, len(sorted_places))]
    for place in top_places:
        try:
            # Get additional details
            details = gmaps.place(place_id=place['place_id'], fields=[
                'name', 'rating', 'user_ratings_total', 'formatted_address',
                'formatted_phone_number', 'website', 'opening_hours',
                'price_level', 'review', 'photo', 'type', 'url'
            ])
            
            if 'result' in details:
                detailed_place = {**place, **details['result']}
                detailed_places.append(detailed_place)
        except Exception as e:
            # If we can't get details, just use the basic place data
            detailed_places.append(place)
    
    return detailed_places

# Function to get place recommendations with travel style preference
def get_recommendations(category, location_name, location_coords, gmaps, llm, travel_style="Any"):
    """
    Get recommendations for a specific category at a location, filtered by travel style
    """
    # Get enhanced place data
    places = enhanced_place_search(category, location_coords, location_name, gmaps, travel_style, radius=5000, limit=10)
    
    # Process places for display
    processed_places = []
    
    for place in places:
        # Extract relevant information
        processed_place = {
            "name": place.get("name", "Unknown"),
            "rating": place.get("rating", "N/A"),
            "total_ratings": place.get("user_ratings_total", 0),
            "address": place.get("vicinity", place.get("formatted_address", "Address not available")),
            "place_id": place.get("place_id", ""),
            "types": place.get("types", []),
            "location": place.get("geometry", {}).get("location", {}),
            "price_level": place.get("price_level", None),
            "opening_hours": place.get("opening_hours", {}).get("weekday_text", []),
            "photos": place.get("photos", []),
            "url": place.get("url", ""),
            "website": place.get("website", "")
        }
        
        # Add current open status
        if "opening_hours" in place and "open_now" in place["opening_hours"]:
            processed_place["open_now"] = place["opening_hours"]["open_now"]
        else:
            processed_place["open_now"] = None
            
        processed_places.append(processed_place)
    
    # Use LLM to enhance the recommendations with personalized descriptions
    if processed_places:
        # Create a template for the recommendations that includes travel style
        recommendation_template = """
            You are a travel expert specializing in {category} recommendations.
            Based on the following places in {location_name}, provide brief recommendations
            aligned with a {travel_style} travel style.

            For each place, write one concise sentence describing what makes it special.
            Keep descriptions short but informative.

            Places data: {places_data}

            FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with this structure:
            {{
                "recommendations": [
                    {{
                        "place_id": "the place_id",
                        "name": "Place Name",
                        "description": "Brief description",
                        "highlights": ["Highlight 1", "Highlight 2"]
                    }}
                ]
            }}

            Limit to 2-3 highlights per place. Be very concise.
            """
        
        recommendation_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=["category", "location_name", "travel_style", "places_data"],
                template=recommendation_template
            )
        )
        
        # Get enhanced recommendations
        try:
            simplified_places = []
            for place in processed_places[:10]:
                simplified_place = {
                    "place_id": place.get("place_id", ""),
                    "name": place.get("name", "Unknown"),
                    "rating": place.get("rating", "N/A"),
                    "total_ratings": place.get("total_ratings", 0),
                    "address": place.get("address", ""),
                    "types": place.get("types", [])[:3],  # Just first 3 types
                    "price_level": place.get("price_level", None)
                }
                simplified_places.append(simplified_place)
            
            enhanced_results = recommendation_chain.run({
                "category": category,
                "location_name": location_name,
                "travel_style": travel_style,
                "places_data": json.dumps(simplified_places)
            })
            
            # Process the LLM response
            try:
                # Extract the JSON from the response
                # First try direct JSON parsing
                recommendations = json.loads(enhanced_results)
                
                # If that fails, try to extract JSON from text
                if not isinstance(recommendations, dict):
                    start_idx = enhanced_results.find('{')
                    end_idx = enhanced_results.rfind('}') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_result = enhanced_results[start_idx:end_idx]
                        recommendations = json.loads(json_result)
                
                # Merge the enhanced descriptions with the original place data
                if "recommendations" in recommendations and isinstance(recommendations["recommendations"], list):
                    enhanced_places = []
                    rec_dict = {r["place_id"]: r for r in recommendations["recommendations"]}
                    
                    for place in processed_places:
                        if place["place_id"] in rec_dict:
                            # Add the description and highlights
                            place["description"] = rec_dict[place["place_id"]].get("description", "")
                            place["highlights"] = rec_dict[place["place_id"]].get("highlights", [])
                        else:
                            place["description"] = ""
                            place["highlights"] = []
                        enhanced_places.append(place)
                    
                    return enhanced_places
            except json.JSONDecodeError as je:
                st.error(f"Error parsing LLM response as JSON: {str(je)}")
                st.write("LLM Response:", enhanced_results)
        except Exception as e:
            st.error(f"Error enhancing recommendations: {str(e)}")
            # Fall back to the processed places without enhancements
            
    return processed_places

# Fallback description generation function that includes travel style
def generate_simple_descriptions(places, category, location_name, travel_style="Any"):
    """Generate simple descriptions for places if LLM enhancement fails"""
    for place in places:
        # Create a simple description based on available data
        rating_text = ""
        if place.get("rating", 0) >= 4.5:
            rating_text = "highly-rated"
        elif place.get("rating", 0) >= 4.0:
            rating_text = "well-rated"
        
        type_text = ""
        if place.get("types"):
            place_types = [t.replace("_", " ") for t in place.get("types", [])[:2]]
            if place_types:
                type_text = f"{', '.join(place_types)}"
        
        # Include travel style in description
        style_text = ""
        if travel_style != "Any":
            style_text = f"for {travel_style} travelers "
        
        # Generate description
        if rating_text and type_text:
            place["description"] = f"A {rating_text} {type_text} in {location_name}. Great choice {style_text}for {category} enthusiasts."
        elif rating_text:
            place["description"] = f"A {rating_text} establishment in {location_name}. Worth checking out {style_text}during your visit."
        else:
            place["description"] = f"An interesting {category} option in {location_name} {style_text}."
        
        # Generate simple highlights
        highlights = []
        if place.get("rating", 0) >= 4.0:
            highlights.append(f"Rated {place.get('rating', 'N/A')}/5 by {place.get('total_ratings', 0)} visitors")
        
        if place.get("price_level") is not None:
            price_terms = ["Budget-friendly", "Moderately priced", "Upscale", "Luxury"]
            if place["price_level"] < len(price_terms):
                highlights.append(price_terms[place["price_level"]])
        
        if place.get("open_now") is True:
            highlights.append("Currently open for visitors")
            
        # Add travel style highlight
        if travel_style == "Budget":
            highlights.append("Good value for money")
        elif travel_style == "Mid-range":
            highlights.append("Great balance of quality and price")
        elif travel_style == "Luxury":
            highlights.append("Premium experience")
            
        # Add location-based highlight
        highlights.append(f"Located in {location_name}")
        
        place["highlights"] = highlights
    
    return places

# Add this function to fetch a relevant image based on destination
def get_destination_image(destination_name, gmaps, google_maps_api_key):
    """Fetch an image of the destination using Google Places API"""
    try:
        # Search for the destination
        search_result = gmaps.places(
            query=f"landmark {destination_name}",
            type="tourist_attraction"
        )
        
        # Check if we got results
        if 'results' in search_result and search_result['results']:
            place = search_result['results'][0]
            
            # Try to get a photo reference
            if 'photos' in place and place['photos']:
                photo_reference = place['photos'][0]['photo_reference']
                
                # Use Google Places Photo API to get the image
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1000&photoreference={photo_reference}&key={google_maps_api_key}"
                return photo_url
        
        # Fallback to a generic travel image if no specific image found
        return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1000"
    except Exception as e:
        st.error(f"Error fetching image: {str(e)}")
        return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1000"