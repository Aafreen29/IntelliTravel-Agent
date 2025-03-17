import streamlit as st

# Function to display recommendations in a card-based layout
def display_recommendation_cards(places, category):
    """Display recommendations in a card-based layout similar to Google"""
    if not places:
        st.info(f"No {category} recommendations found for this location.")
        return
    
    # Create 3 columns for cards
    cols = st.columns(3)
    
    # Display each place in a card
    for i, place in enumerate(places):
        col = cols[i % 3]
        
        with col:
            with st.container(border=True):
                # Display place name
                st.subheader(place.get('name', 'Unknown Place'))
                
                # Display rating with stars
                rating = place.get('rating', 0)
                if rating:
                    rating_stars = "★" * int(rating) + "☆" * (5 - int(rating))
                    rating_str = f"{rating}/5.0 ({rating_stars}) • {place.get('total_ratings', 0)} reviews"
                    st.write(rating_str)
                
                # Price level
                price_level = place.get('price_level', None)
                if price_level is not None:
                    st.write("".join(["$" for _ in range(price_level)]))
                
                # Open status
                if place.get('open_now') is not None:
                    status = "🟢 Open now" if place['open_now'] else "🔴 Closed"
                    st.write(status)
                
                # Description (from LLM)
                if place.get('description'):
                    st.write(place['description'])
                
                # Highlights
                if place.get('highlights') and len(place['highlights']) > 0:
                    st.write("**Highlights:**")
                    for highlight in place['highlights'][:3]:
                        st.write(f"• {highlight}")
                
                # Address
                st.write(f"📍 {place.get('address', 'Address not available')}")
                
                # Links
                cols2 = st.columns(2)
                if place.get('website'):
                    cols2[0].link_button("Website", place['website'])
                if place.get('url'):
                    cols2[1].link_button("Google Maps", place['url'])
        
        # Only show the first 9 places to avoid overcrowding
        if i >= 9:
            st.info(f"Showing top {i+1} recommendations.")
            break