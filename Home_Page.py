import streamlit as st
import requests
import google.generativeai as genai
import os
import io
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus, urlencode
import time
import random
import json
import logging
import numpy as np
import matplotlib.patches as mpatches
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Streamlit page
st.set_page_config(
    page_title="DeepBrush - AI Art Docent",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Font Settings */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Poppins:wght@300;400;500;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Header - Artistic Style */
    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 2rem auto 1.5rem auto !important;
        text-align: center !important;
        letter-spacing: 0.05em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .main-header::after {
        content: "";
        display: block;
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, #3B82F6, #1E3A8A);
        margin: 0.5rem auto 0 auto;
        border-radius: 2px;
    }
    
    /* Sub-header - Elegant Style */
    .sub-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.7rem !important;
        font-weight: 500 !important;
        color: #4B5563 !important;
        margin-bottom: 2.5rem !important;
        text-align: center !important;
        font-style: italic;
        opacity: 0.85;
    }
    
    /* Info Box - Refined Design */
    .info-box {
        background: linear-gradient(145deg, #F9FAFB, #F3F4F6);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.05), 
                   -5px -5px 15px rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.7);
    }
    
    /* Result Header - Artistic Style */
    .result-header {
        font-family: 'Playfair Display', serif;
        font-size: 2rem !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 2rem 0 1.5rem 0 !important;
        position: relative;
        padding-bottom: 0.5rem;
    }
    
    .result-header::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #3B82F6, transparent);
    }
    
    /* Insight Box - Creative Style */
    .insight-box {
        background: linear-gradient(to right, #EFF6FF 0%, #F9FAFB 100%);
        border-left: 5px solid #3B82F6;
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .insight-box::before {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), transparent);
        border-radius: 0 0 0 60px;
    }
    
    /* Classification Box - Artistic Style */
    .classification-box {
        background: linear-gradient(to right, #ECFDF5 0%, #F0FDF9 100%);
        border-left: 5px solid #10B981;
        padding: 20px;
        margin: 20px 0;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.3rem;
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.1);
        position: relative;
    }
    
    .classification-box::after {
        content: "";
        position: absolute;
        bottom: 0;
        right: 0;
        width: 100px;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.5));
    }
    
    /* Analysis Section - Refined Style */
    .analysis-section {
        margin: 30px 0;
        border-bottom: 1px solid rgba(229, 231, 235, 0.7);
        padding-bottom: 25px;
        position: relative;
    }
    
    .analysis-section::before {
        content: "";
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 100px;
        height: 3px;
        background: linear-gradient(90deg, #1E3A8A, transparent);
        border-radius: 3px;
    }
    
    /* Analysis Title - Elegant Style */
    .analysis-title {
        font-family: 'Playfair Display', serif;
        color: #1E3A8A;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 15px;
        position: relative;
        display: inline-block;
    }
    
    .analysis-title::after {
        content: "";
        position: absolute;
        bottom: -5px;
        left: 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, #3B82F6, transparent);
    }
    
    /* Visualization Container - Artistic Style */
    .visualization-container {
        background: linear-gradient(145deg, #FFFFFF, #F9FAFB);
        padding: 30px;
        border-radius: 16px;
        margin: 30px 0;
        box-shadow: 8px 8px 16px rgba(0, 0, 0, 0.05), 
                   -8px -8px 16px rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.6);
    }
    
    /* Beautiful Horizontal Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: linear-gradient(145deg, #F9FAFB, #F3F4F6);
        padding: 10px 15px 0px 15px;
        border-radius: 12px 12px 0 0;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.7);
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px 10px 0 0;
        background: transparent;
        padding: 0px 20px;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        color: #4B5563;
        border: 1px solid transparent;
        border-bottom: none;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #3B82F6, #1E3A8A);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        transform: scaleX(0.8);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
        border-color: rgba(230, 232, 236, 0.5);
        color: #1E3A8A;
        font-weight: 600;
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.02);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"]::before {
        transform: scaleX(1);
        height: 3px;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background: white;
        border-radius: 0 0 12px 12px;
        padding: 20px;
        border: 1px solid rgba(230, 232, 236, 0.5);
        border-top: none;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
    }
    
    /* Button Styling */
    .stButton button {
        background: linear-gradient(135deg, #3B82F6 0%, #1E3A8A 100%);
        color: white;
        border-radius: 8px;
        padding: 10px 25px;
        font-weight: 500;
        border: none;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
    }
    
    .stButton button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.4);
    }
    
    /* Input Field Styling */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        border-radius: 8px;
        border: 1px solid rgba(203, 213, 225, 0.8);
        padding: 10px 15px;
        transition: all 0.3s ease;
        box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.02);
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Select Box Styling */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
    }
    
    .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Checkboxes and Radio Buttons */
    .stCheckbox [data-baseweb="checkbox"], .stRadio [data-baseweb="radio"] {
        margin-bottom: 10px;
    }
    
    /* Panel Styling for Cards */
    .css-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid rgba(230, 232, 236, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .css-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background-color: #3B82F6;
        background-image: linear-gradient(45deg, 
                                        #3B82F6 25%, 
                                        #60A5FA 25%, 
                                        #60A5FA 50%, 
                                        #3B82F6 50%, 
                                        #3B82F6 75%, 
                                        #60A5FA 75%, 
                                        #60A5FA);
        background-size: 20px 20px;
        animation: progress-animation 2s linear infinite;
    }
    
    @keyframes progress-animation {
        0% {
            background-position: 0 0;
        }
        100% {
            background-position: 40px 0;
        }
    }
    
    /* Slider */
    .stSlider [data-baseweb="slider"] {
        height: 6px;
    }
    
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        background: linear-gradient(135deg, #3B82F6 0%, #1E3A8A 100%);
        border: 2px solid white;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #3B82F6, #1E3A8A);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #2563EB, #1E40AF);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        color: #1E3A8A;
        background: linear-gradient(90deg, rgba(239, 246, 255, 0.8), transparent);
        border-radius: 8px;
        padding-left: 10px !important;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #1E3A8A !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
    }
    
    /* Dataframe / Table styling */
    .stDataFrame {
        border: none !important;
    }
    
    .stDataFrame [data-testid="stTable"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    
    .stDataFrame thead tr {
        background: linear-gradient(90deg, #EFF6FF, #F9FAFB) !important;
        color: #1E3A8A !important;
    }
    
    .stDataFrame thead th {
        padding: 12px 24px !important;
        border-bottom: 2px solid #E5E7EB !important;
        font-weight: 600 !important;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #F9FAFB !important;
    }
    
    .stDataFrame tbody tr:hover {
        background-color: #EFF6FF !important;
    }
    
    .stDataFrame tbody td {
        padding: 10px 24px !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    
    /* App background and content container */
    .reportview-container {
        background: linear-gradient(135deg, rgba(249, 250, 251, 0.5) 0%, rgba(243, 244, 246, 0.5) 100%);
    }
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# Gemini API Key
GEMINI_API_KEY = "AIzaSyDVh44jf0dulFB1qP8FwnrHb92DY9gBfdU"  # Replace with your API key
genai.configure(api_key=GEMINI_API_KEY)

# Function to classify artwork type
def classify_artwork_type(image_data):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    You are DeepBrush, an expert art historian. Carefully analyze this image and classify it as ONE of the following artwork types:
    - Drawing
    - Painting
    - Sculpture
    - Engraving
    - Iconography
    - Mixed Media
    
    Make your determination based on medium, technique, and visual characteristics.
    
    Respond with ONLY the classification word, nothing else. For example: "Painting"
    """
    
    image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
    try:
        response = model.generate_content([prompt, image_parts])
        artwork_type = response.text.strip()
        # Ensure it's one of the valid types
        valid_types = ["Drawing", "Painting", "Sculpture", "Engraving", "Iconography", "Mixed Media"]
        if artwork_type not in valid_types:
            artwork_type = "Painting"  # Default to Painting if response is invalid
        return artwork_type.lower()
    except Exception as e:
        logger.error(f"Error in artwork classification: {e}")
        return "painting"  # Default to painting on error

# Set up logging
logger = logging.getLogger(__name__)

def analyze_artwork(image_data, artwork_type):
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are DeepBrush, an expert art historian and docent with extensive knowledge of {artwork_type}s and art history.
    
    Analyze this {artwork_type} in detail and provide the following information in a structured format:
    
    ## Title and Artist
    [Provide the most likely title prediction and artist identification]
    
    ## Art Style & Period Classification
    [Identify the artistic movement, period, and specific style]
    
    ## Detailed Visual Analysis
    [Describe the composition, color palette, techniques, materials, and visual elements in detail]
    
    ## Contextual Analysis
    [Explain the historical context, symbolism, and cultural significance]
    
    ## Similar Works
    [Mention other artworks that share stylistic elements or themes]
    
    ## Technical Features
    [Highlight unique technical aspects of this {artwork_type}]
    
    Be specific, informative, and insightful. Use markdown formatting to structure your response.
    """
    
    # Convert image to base64
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    image_part = {"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}}
    
    try:
        response = model.generate_content([prompt, image_part])
        return response.text if response else "Error: No response from AI."
    except Exception as e:
        logger.error(f"Error in Art analysis: {e}")
        return "Error analyzing artwork. Please try again."

# Function to get artist and artwork details for further searches
def extract_artist_and_title(analysis):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    From the following art analysis, extract only the artist name and the artwork title. 
    If multiple possible artists or titles are mentioned, choose the most likely one.
    If the artist or title is unknown or uncertain, say "Unknown" for that field.
    
    Format your response exactly like this, nothing more:
    Artist: [Artist Name]
    Title: [Artwork Title]
    
    Here's the analysis:
    {analysis}
    """
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        artist_match = re.search(r"Artist: (.+)", result)
        title_match = re.search(r"Title: (.+)", result)
        
        artist = artist_match.group(1) if artist_match else "Unknown"
        title = title_match.group(1) if title_match else "Unknown"
        
        if artist == "Unknown" and title == "Unknown":
            # Try to extract something that could be used for searching
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = """
            From the art analysis provided, extract key terms that could be used for searching 
            this artwork online, such as distinctive style, period, subject matter, or technique.
            Format your response as: "Search terms: [term1], [term2], [term3]"
            
            Analysis:
            """ + analysis
            
            response = model.generate_content(prompt)
            terms_match = re.search(r"Search terms: (.+)", response.text)
            search_terms = terms_match.group(1) if terms_match else ""
            return artist, title, search_terms
        
        return artist, title, ""
    except Exception as e:
        logger.error(f"Error extracting artist and title: {e}")
        return "Unknown", "Unknown", ""

# Advanced Web Scraping function
def scrape_art_insights(artist, title, search_terms=""):
    insights = []
    
    if artist == "Unknown" and title == "Unknown" and search_terms:
        search_query = f"{search_terms} art analysis"
    else:
        search_query = f"{artist} {title} art analysis"
    
    encoded_query = quote_plus(search_query)
    
    try:
        # User agents to rotate for avoiding detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        ]
        
        # First, try to get results from Wikipedia API
        wiki_insights = scrape_wikipedia(artist, title)
        if wiki_insights:
            insights.extend(wiki_insights)
        
        # Then try scraping from Google search results
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Google search URL
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            search_results = soup.select('div.g')
            
            # Process top 5 results (or fewer if less available)
            for i, result in enumerate(search_results[:5]):
                try:
                    # Extract title
                    title_elem = result.select_one('h3')
                    if not title_elem:
                        continue
                    
                    title_text = title_elem.get_text()
                    
                    # Extract URL
                    url_elem = result.select_one('a')
                    if not url_elem:
                        continue
                    
                    url = url_elem.get('href')
                    if url.startswith('/url?'):
                        url = re.search(r'/url\?q=([^&]+)', url).group(1)
                    
                    # Extract snippet
                    snippet_elem = result.select_one('div.VwiC3b')
                    snippet = snippet_elem.get_text() if snippet_elem else "No preview available."
                    
                    # Skip irrelevant or unwanted sites (e.g., shopping sites)
                    skip_domains = ['amazon.com', 'ebay.com', 'etsy.com', 'pinterest.com']
                    if any(domain in url for domain in skip_domains):
                        continue
                    
                    # Only use snippet if it's substantive
                    if len(snippet) > 50:
                        source = title_text.split(' - ')[0] if ' - ' in title_text else title_text
                        
                        insights.append({
                            "source": source[:50],  # Limit source length
                            "text": snippet[:300] + "...",  # Limit text length
                            "url": url
                        })
                except Exception as e:
                    logger.warning(f"Error processing search result: {e}")
                    continue
            
            # If we didn't get enough insights, try additional art-specific sites
            if len(insights) < 3:
                art_sites = ['metmuseum.org', 'moma.org', 'tate.org.uk', 'nationalgallery.org.uk', 'artic.edu']
                
                for site in art_sites:
                    site_query = f"{search_query} site:{site}"
                    encoded_site_query = quote_plus(site_query)
                    site_search_url = f"https://www.google.com/search?q={encoded_site_query}"
                    
                    try:
                        # Add delay to avoid rate limiting
                        time.sleep(1)
                        
                        site_response = requests.get(site_search_url, headers={'User-Agent': random.choice(user_agents)}, timeout=10)
                        
                        if site_response.status_code == 200:
                            site_soup = BeautifulSoup(site_response.text, 'html.parser')
                            site_results = site_soup.select('div.g')
                            
                            if site_results:
                                result = site_results[0]  # Just take the first result
                                
                                title_elem = result.select_one('h3')
                                url_elem = result.select_one('a')
                                snippet_elem = result.select_one('div.VwiC3b')
                                
                                if title_elem and url_elem and snippet_elem:
                                    title_text = title_elem.get_text()
                                    url = url_elem.get('href')
                                    if url.startswith('/url?'):
                                        url = re.search(r'/url\?q=([^&]+)', url).group(1)
                                    
                                    snippet = snippet_elem.get_text()
                                    
                                    source = title_text.split(' - ')[0] if ' - ' in title_text else title_text
                                    
                                    insights.append({
                                        "source": source[:50],
                                        "text": snippet[:300] + "...",
                                        "url": url
                                    })
                                    
                                    # If we have enough insights, break out
                                    if len(insights) >= 5:
                                        break
                    except Exception as e:
                        logger.warning(f"Error scraping art site {site}: {e}")
                        continue
        
        # If we still don't have enough insights, add some generic ones
        if not insights:
            if artist != "Unknown":
                insights.append({
                    "source": "DeepBrush Analysis",
                    "text": f"Based on stylistic analysis, this work appears to be by {artist}. Further research is recommended to confirm attribution.",
                    "url": f"https://www.google.com/search?q={quote_plus(artist)}"
                })
            else:
                insights.append({
                    "source": "DeepBrush Analysis",
                    "text": "This artwork shows interesting stylistic elements that warrant further investigation. Consider consulting an art historian for more detailed analysis.",
                    "url": f"https://www.google.com/search?q={quote_plus(search_query)}"
                })
        
        return insights, search_query
    
    except Exception as e:
        logger.error(f"Error while scraping insights: {e}")
        # Return fallback insights if scraping fails
        fallback_insights = [{
            "source": "DeepBrush Analysis",
            "text": "Web search encountered an error. This artwork appears to have significant artistic merit and historical context worth exploring further.",
            "url": f"https://www.google.com/search?q={encoded_query}"
        }]
        return fallback_insights, search_query

# Helper function to scrape Wikipedia
def scrape_wikipedia(artist, title):
    insights = []
    
    if artist == "Unknown":
        return []
    
    try:
        # First try the artist page
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&titles={quote_plus(artist)}"
        response = requests.get(wiki_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            # Get the first page (there should only be one)
            if pages:
                page_id = list(pages.keys())[0]
                if page_id != '-1':  # -1 means no results
                    extract = pages[page_id].get('extract', '')
                    if extract:
                        # Trim to reasonable length
                        if len(extract) > 500:
                            extract = extract[:500] + "..."
                        
                        insights.append({
                            "source": "Wikipedia - Artist",
                            "text": extract,
                            "url": f"https://en.wikipedia.org/wiki/{quote_plus(artist)}"
                        })
        
        # Then try the artwork title if it's not "Unknown"
        if title != "Unknown":
            title_wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&titles={quote_plus(title)}"
            title_response = requests.get(title_wiki_url, timeout=10)
            
            if title_response.status_code == 200:
                title_data = title_response.json()
                title_pages = title_data.get('query', {}).get('pages', {})
                
                if title_pages:
                    title_page_id = list(title_pages.keys())[0]
                    if title_page_id != '-1':
                        title_extract = title_pages[title_page_id].get('extract', '')
                        if title_extract:
                            if len(title_extract) > 500:
                                title_extract = title_extract[:500] + "..."
                            
                            insights.append({
                                "source": "Wikipedia - Artwork",
                                "text": title_extract,
                                "url": f"https://en.wikipedia.org/wiki/{quote_plus(title)}"
                            })
        
        return insights
    
    except Exception as e:
        logger.warning(f"Error scraping Wikipedia: {e}")
        return []

# Enhanced function to create more informative visualization
def create_visualization(analysis, artwork_type):
    # Extract relevant information for visualization using Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    From the following art analysis of a {artwork_type}, extract detailed information for visualization.
    
    1. Identify 5-7 distinctive artistic characteristics or techniques and rate their prominence (1-10)
    2. Identify the color palette (5 main colors used in the artwork)
    3. Identify the emotional or thematic elements (5 elements with their strength 1-10)
    
    Format your response exactly as JSON:
    {{
      "characteristics": ["Characteristic 1", "Characteristic 2", "Characteristic 3", "Characteristic 4", "Characteristic 5"],
      "ratings": [8, 6, 9, 4, 7],
      "colors": ["#C41E3A", "#0077B6", "#FFD700", "#2D3748", "#8B5A2B"],
      "emotions": ["Serenity", "Drama", "Melancholy", "Power", "Mystery"],
      "emotion_ratings": [9, 5, 7, 8, 6]
    }}
    
    Analysis: {analysis}
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Create enhanced visualization with two subplots
            fig = plt.figure(figsize=(16, 10))
            
            # 1. Radar chart for artistic characteristics (left subplot)
            ax1 = fig.add_subplot(121, polar=True)
            
            characteristics = data["characteristics"]
            ratings = data["ratings"]
            
            # Number of variables
            N = len(characteristics)
            
            # What will be the angle of each axis in the plot
            angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Add the ratings to complete the loop
            ratings_plot = ratings + [ratings[0]]
            
            # Draw one axis per variable and add labels
            ax1.plot(angles, ratings_plot, 'o-', linewidth=2)
            ax1.fill(angles, ratings_plot, alpha=0.25)
            
            # Fix axis to go in the right order and start at 12 o'clock
            ax1.set_xticks(angles[:-1])
            ax1.set_xticklabels(characteristics)
            
            # Set y-axis limits
            ax1.set_ylim(0, 10)
            ax1.set_title("Artistic Elements Analysis", size=15, color="#1E3A8A", pad=20)
            
            # 2. Combined chart for colors and emotions (right subplot)
            ax2 = fig.add_subplot(122)
            
            # Get colors from data
            colors = data["colors"]
            emotions = data["emotions"]
            emotion_ratings = data["emotion_ratings"]
            
            # Create mini color swatches
            color_display = np.ones((len(colors), 10, 3))
            for i, color in enumerate(colors):
                # Convert hex to RGB
                r = int(color[1:3], 16) / 255.0
                g = int(color[3:5], 16) / 255.0
                b = int(color[5:7], 16) / 255.0
                color_display[i, :, :] = [r, g, b]
            
            # Plot color swatches as small rectangle in legend
            color_patches = []
            for i, color in enumerate(colors):
                color_patches.append(mpatches.Patch(color=color, label=f"Color {i+1}"))
            
            # Horizontal bar chart for emotions
            y_pos = np.arange(len(emotions))
            ax2.barh(y_pos, emotion_ratings, color='#3B82F6', alpha=0.7)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(emotions)
            ax2.set_xlabel('Intensity (1-10)')
            ax2.set_title('Emotional & Thematic Elements', size=15, color="#1E3A8A")
            ax2.invert_yaxis()  # Labels read top-to-bottom
            
            # Add color legend
            ax2.legend(handles=color_patches, title="Color Palette", 
                    loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
            
            plt.tight_layout(h_pad=2, rect=[0, 0.03, 1, 0.97])
            plt.suptitle(f"Visual Analysis of {artwork_type.title()}", fontsize=18, color="#1E3A8A", y=0.98)
            
            # Return the figure and a description
            description = f"""
            This visualization presents two key aspects of the {artwork_type}:
            
            **Left Chart**: A radar diagram showing the prominence of key artistic elements in the artwork. The higher values (closer to the outer edge) indicate stronger presence of that particular characteristic.
            
            **Right Chart**: Shows the emotional and thematic elements present in the artwork, along with the dominant color palette used by the artist. The bars represent the intensity of each emotional element.
            """
            
            return fig, description
        else:
            # Fallback visualization if parsing fails
            return create_fallback_visualization(artwork_type), "A visual representation of artistic elements present in the artwork."
    
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return create_fallback_visualization(artwork_type), "A visual representation of artistic elements present in the artwork."

def create_fallback_visualization(artwork_type):
    # Create a fallback visualization with more information
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left chart - Artistic elements
    categories = ["Composition", "Color Use", "Technique", "Symbolism", "Historical Impact"]
    values = [7, 8, 6, 9, 5]
    
    sns.barplot(x=categories, y=values, palette="Blues_d", ax=ax1)
    ax1.set_ylim(0, 10)
    ax1.set_title("Artistic Elements Analysis", size=15, color="#1E3A8A")
    ax1.set_ylabel("Prominence (1-10)")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, horizontalalignment='right')
    
    # Right chart - Typical examples of the art form
    art_forms = {
        "painting": ["Oil on Canvas", "Watercolor", "Acrylic", "Mixed Media", "Fresco"],
        "sculpture": ["Marble", "Bronze", "Wood", "Clay", "Mixed Materials"],
        "drawing": ["Pencil", "Charcoal", "Ink", "Pastel", "Mixed Media"],
        "engraving": ["Wood", "Metal", "Linocut", "Etching", "Lithography"],
        "iconography": ["Religious", "Byzantine", "Russian", "Modern", "Symbolic"]
    }
    
    # Get values for the art form or use a default
    form_types = art_forms.get(artwork_type.lower(), ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"])
    form_values = [8, 7, 5, 6, 4]  # Example distribution
    
    sns.barplot(x=form_types, y=form_values, palette="Reds_d", ax=ax2)
    ax2.set_ylim(0, 10)
    ax2.set_title(f"{artwork_type.title()} Techniques", size=15, color="#1E3A8A")
    ax2.set_ylabel("Relevance (1-10)")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, horizontalalignment='right')
    
    plt.tight_layout()
    plt.suptitle(f"Visual Analysis of {artwork_type.title()}", fontsize=18, color="#1E3A8A", y=0.98)
    
    return fig

# Function to get relevant links
def get_relevant_links(artist, title, search_terms=""):
    search_query = f"{artist} {title} artwork"
    
    if artist == "Unknown" and title == "Unknown" and search_terms:
        search_query = f"{search_terms} artwork"
    
    links = []
    
    try:
        # Actually search for relevant links
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Search specifically on art websites
        art_sites = [
            {"name": "Google Arts & Culture", "domain": "artsandculture.google.com"},
            {"name": "Metropolitan Museum of Art", "domain": "metmuseum.org"},
            {"name": "Museum of Modern Art", "domain": "moma.org"},
            {"name": "WikiArt", "domain": "wikiart.org"},
            {"name": "National Gallery", "domain": "nationalgallery.org.uk"},
            {"name": "Art Institute of Chicago", "domain": "artic.edu"}
        ]
        
        for site in art_sites[:3]:  # Limit to 3 sites to avoid too many requests
            search_site_query = f"{search_query} site:{site['domain']}"
            encoded_query = quote_plus(search_site_query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            try:
                # Add delay to avoid rate limiting
                time.sleep(1)
                
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.select('div.g')
                    
                    for i, result in enumerate(results[:2]):  # Get top 2 results per site
                        title_elem = result.select_one('h3')
                        url_elem = result.select_one('a')
                        
                        if title_elem and url_elem:
                            result_title = title_elem.get_text()
                            url = url_elem.get('href')
                            
                            if url.startswith('/url?'):
                                url = re.search(r'/url\?q=([^&]+)', url).group(1)
                            
                            links.append({
                                "title": f"{result_title} - {site['name']}",
                                "url": url
                            })
            except Exception as e:
                logger.warning(f"Error getting links from {site['name']}: {e}")
                continue
        
        # Add Wikipedia if the artist is known
        if artist != "Unknown":
            links.append({
                "title": f"{artist} - Wikipedia",
                "url": f"https://en.wikipedia.org/wiki/{quote_plus(artist)}"
            })
        
        # If no links were found, provide some general art resource links
        if not links:
            links = [
                {"title": "Art History Resources", "url": "https://arthistoryresources.net/"},
                {"title": "Google Arts & Culture", "url": "https://artsandculture.google.com/"},
                {"title": "The Metropolitan Museum of Art", "url": "https://www.metmuseum.org/"}
            ]
        
        return links, search_query
    
    except Exception as e:
        logger.error(f"Error getting relevant links: {e}")
        # Fallback links
        fallback_links = [
            {"title": "Art History Resources", "url": "https://arthistoryresources.net/"},
            {"title": "Google Arts & Culture", "url": "https://artsandculture.google.com/"},
            {"title": "The Metropolitan Museum of Art", "url": "https://www.metmuseum.org/"}
        ]
        return fallback_links, search_query

# Main application
def main():
    st.markdown("<h1 class='main-header'>DeepBrush</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your AI Art Docent Made by Akshara</p>", unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📋 DeepBrush")
    st.sidebar.markdown("### Your AI Art History Guide")
    
    # File uploader in sidebar
    uploaded_file = st.sidebar.file_uploader("Upload an artwork image", type=["jpg", "jpeg", "png"])
    
    # Instructions in sidebar
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("""
    1. Upload an image of any artwork
    2. Wait for AI analysis (may take a moment)
    3. Explore the comprehensive art analysis and insights
    """)
    
    # About section in sidebar
    st.sidebar.markdown("### About")
    st.sidebar.markdown("""
    DeepBrush uses Advance AI to analyze artwork 
    and provide detailed insights about style, artist, 
    historical context, and more.
    """)
    
    # Main content area
    if uploaded_file is None:
        # Display welcome content when no file is uploaded
        st.markdown("""
        <div class="info-box">
            <h2>Welcome to DeepBrush!</h2>
            <p>Upload an image of any artwork to receive a detailed analysis including:</p>
            <ul>
                <li>Artwork classification and identification</li>
                <li>Style and period classification</li>
                <li>Detailed visual analysis</li>
                <li>Historical and cultural context</li>
                <li>Comparative analysis with similar works</li>
                <li>Technical insights and visualizations</li>
            </ul>
            <p>Start by uploading an image using the sidebar on the left.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample images
        st.markdown("### Example Analyses")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg", 
                    caption="Renaissance Painting")
        with col2:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/800px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg", 
                    caption="Post-Impressionist Painting")
        with col3:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/The_Scream.jpg/800px-The_Scream.jpg", 
                    caption="Expressionist Painting")
    
    else:
        try:
            # Process the uploaded image
            image_bytes = uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Display the uploaded image
            st.image(image, caption="Uploaded Artwork", use_container_width=True)
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "🌐 Web Insights", "📈 Visualization", "🔗 Resources"])
            
            with st.spinner("Analyzing artwork..."):
                # Classify artwork type
                artwork_type = classify_artwork_type(image_bytes)
                
                # Get the complete artwork analysis
                analysis = analyze_artwork(image_bytes, artwork_type)
                
                # Extract artist and title for further searches
                artist, title, search_terms = extract_artist_and_title(analysis)
                
                # Tab 1: Main Analysis
                with tab1:
                    st.markdown(f"<div class='classification-box'>Artwork Type: {artwork_type.title()}</div>", unsafe_allow_html=True)
                    st.markdown(analysis)
                
                # Tab 2: Web Insights
                with tab2:
                    insights, search_query = scrape_art_insights(artist, title, search_terms)
                    
                    st.markdown("<h2 class='result-header'>Web Insights</h2>", unsafe_allow_html=True)
                    st.markdown(f"Based on search: **{search_query}**")
                    
                    if insights:
                        for insight in insights:
                            st.markdown(f"""
                            <div class="insight-box">
                                <strong>{insight['source']}</strong><br>
                                {insight['text']}<br>
                                <a href="{insight['url']}" target="_blank">Source Link</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("No additional web insights found.")
                
                # Tab 3: Visualization
                with tab3:
                    st.markdown("<h2 class='result-header'>Visual Analysis</h2>", unsafe_allow_html=True)
                    
                    # Create visualization
                    fig, viz_description = create_visualization(analysis, artwork_type)
                    
                    # Display visualization
                    st.pyplot(fig)
                    st.markdown(viz_description)
                
                # Tab 4: Resources
                with tab4:
                    st.markdown("<h2 class='result-header'>Further Resources</h2>", unsafe_allow_html=True)
                    
                    # Get relevant links
                    links, search_query = get_relevant_links(artist, title, search_terms)
                    
                    st.markdown(f"Based on search: **{search_query}**")
                    
                    if links:
                        for link in links:
                            st.markdown(f"[{link['title']}]({link['url']})")
                    else:
                        st.markdown("No specific resources found.")
                    
                    # Add options for further exploration
                    st.markdown("### Explore More")
                    st.markdown("""
                    - [Google Arts & Culture](https://artsandculture.google.com/)
                    - [WikiArt](https://www.wikiart.org/)
                    - [The Metropolitan Museum of Art](https://www.metmuseum.org/)
                    - [Museum of Modern Art](https://www.moma.org/)
                    """)
                    
                    # Add export options
                    st.download_button(
                        label="Export Analysis as Text",
                        data=analysis,
                        file_name=f"{artist}_{title}_analysis.txt",
                        mime="text/plain"
                    )
        
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            st.markdown("""
            <div class="info-box">
                <h3>Troubleshooting Tips:</h3>
                <ul>
                    <li>Ensure the uploaded image is clear and focused on the artwork</li>
                    <li>Try with a different image format (JPG, PNG)</li>
                    <li>Make sure the image size is not too large (< 5MB recommended)</li>
                    <li>Check your internet connection</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()