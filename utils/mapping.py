import folium
from streamlit_folium import folium_static

# Function to display map with markers
def display_recommendation_map(places, location_name, center_coords):
    """Display a Folium map with markers for the recommended places"""
    if not places or not center_coords:
        return
    
    # Create a Folium map centered on the location
    m = folium.Map(location=[center_coords['lat'], center_coords['lng']], zoom_start=13)
    
    # Add a marker for the central location
    folium.Marker(
        location=[center_coords['lat'], center_coords['lng']],
        popup=f"<strong>{location_name}</strong>",
        tooltip=location_name,
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Add markers for each place
    for i, place in enumerate(places):
        if 'location' in place and 'lat' in place['location'] and 'lng' in place['location']:
            place_lat = place['location']['lat']
            place_lng = place['location']['lng']
            place_name = place.get('name', f'Location {i+1}')
            
            # Format types for display
            place_types = []
            for t in place.get('types', [])[:3]:
                if t and not t.startswith('establishment'):
                    place_types.append(t.replace('_', ' ').title())
            
            type_str = ", ".join(place_types) if place_types else "Place"
            
            # Format price level
            price_level = place.get('price_level', None)
            if price_level is not None:
                price_display = "".join(["$" for _ in range(price_level)])
            else:
                price_display = "Price not available"
            
            # Create popup content with more details
            popup_html = f"""
            <strong>{place_name}</strong><br>
            Type: {type_str}<br>
            Rating: {place.get('rating', 'N/A')}/5.0 ({place.get('total_ratings', 0)} ratings)<br>
            {price_display}<br>
            {place.get('address', 'Address not available')}<br>
            """
            
            # Add open now status if available
            if place.get('open_now') is not None:
                status = "Open now" if place['open_now'] else "Closed"
                popup_html += f"Status: {status}<br>"
            
            # Add website if available
            if place.get('website'):
                popup_html += f'<a href="{place["website"]}" target="_blank">Website</a><br>'
            
            # Add Google Maps link
            if place.get('url'):
                popup_html += f'<a href="{place["url"]}" target="_blank">View on Google Maps</a>'
            
            # Determine icon color based on rating
            rating = place.get('rating', 0)
            icon_color = 'green' if rating >= 4.5 else 'blue' if rating >= 4.0 else 'orange' if rating >= 3.5 else 'gray'
            
            folium.Marker(
                location=[place_lat, place_lng],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=place_name,
                icon=folium.Icon(color=icon_color)
            ).add_to(m)
    
    # Add a circle showing the search radius
    folium.Circle(
        location=[center_coords['lat'], center_coords['lng']],
        radius=5000,  # 5km radius
        color='blue',
        fill=True,
        fill_opacity=0.1
    ).add_to(m)
    
    # Display the map
    folium_static(m)