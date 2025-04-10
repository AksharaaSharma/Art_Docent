import streamlit as st
import requests
import google.generativeai as genai
import os
import io
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
from Frontend import frontend
import tempfile
import moviepy as mp
from moviepy.editor import TextClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import traceback
from moviepy.video.fx import *


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

frontend()

# Gemini API Key
GEMINI_API_KEY = "AIzaSyDVh44jf0dulFB1qP8FwnrHb92DY9gBfdU"  # Replace with your API key
genai.configure(api_key=GEMINI_API_KEY)

def generate_art_video(image_data, analysis, artwork_type, artist, title):
    try:
        # Create a temporary directory to store our assets
        temp_dir = tempfile.mkdtemp()
        
        # Create the original image file
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('RGB')
        img_path = os.path.join(temp_dir, "artwork.jpg")
        img.save(img_path)
        
        # Extract key sections from the analysis using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        From the following art analysis, extract 5 key points that would be interesting to highlight in a video. 
        Each point should be 1-2 sentences long.
        
        Format as a JSON array of strings:
        ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"]
        
        Analysis: {analysis}
        """
        
        try:
            response = model.generate_content(prompt)
            json_match = re.search(r"\[.*\]", response.text, re.DOTALL)
            if json_match:
                key_points = json.loads(json_match.group(0))
            else:
                # Fallback points
                key_points = [
                    f"This {artwork_type} showcases remarkable artistic technique.",
                    f"The composition draws the viewer's eye to key focal points.",
                    "The color palette creates a distinct emotional atmosphere.",
                    "Notice the unique brushwork and texturing techniques.",
                    "Historical context adds deeper meaning to this piece."
                ]
        except Exception as e:
            st.error(f"Error extracting key points: {e}")
            key_points = [
                f"This {artwork_type} showcases remarkable artistic technique.",
                f"The composition draws the viewer's eye to key focal points.",
                "The color palette creates a distinct emotional atmosphere.",
                "Notice the unique brushwork and texturing techniques.",
                "Historical context adds deeper meaning to this piece."
            ]
        
        # Generate artistic variations of the image
        variations = generate_image_variations(img, temp_dir)
        
        # Create intro image with text instead of TextClip
        intro_text = f"Exploring\n{title if title != 'Unknown' else 'This Artwork'}"
        artist_text = f"By {artist}" if artist != "Unknown" else f"A fascinating {artwork_type}"
        
        # Create intro image
        intro_image_path = create_text_image(intro_text, (1080, 1080), 70, temp_dir, "intro.png")
        intro_clip = ImageClip(intro_image_path, duration=3)
        
        # Create artist image
        artist_image_path = create_text_image(artist_text, (1080, 1080), 70, temp_dir, "artist.png")
        artist_clip = ImageClip(artist_image_path, duration=3)
        
        # Create the main artwork clip with zooming effect
        artwork_clip = ImageClip(img_path, duration=5)
        
        # If the image is wider than 1080, we'll need to pan across it
        if artwork_clip.w > 1080:
            # Create a panning effect from left to right
            def pan(t):
                max_pan = max(0, artwork_clip.w - 1080)
                return ('center', 'center', min(max_pan, max_pan * t / 5))
            
            artwork_clip = artwork_clip.with_position(pan)
        else:
            # Center the image and add a zoom effect
            artwork_clip = artwork_clip.with_position('center')
            

        
        # Create clips for each key point
        point_clips = []
        for i, point in enumerate(key_points):
            # Use a different variation for each point
            var_idx = i % len(variations)
            var_img_path = variations[var_idx]
            
            # Create a clip with the image and text overlay
            img_with_text_path = add_text_to_image(var_img_path, point, temp_dir, f"point_{i}.png")
            
            point_clip = ImageClip(img_with_text_path, duration=5)
            
            point_clips.append(point_clip)
        
        # Create outro image with text
        outro_text = "DeepBrush AI Art Analysis"
        outro_image_path = create_text_image(outro_text, (1080, 1080), 70, temp_dir, "outro.png")
        outro_clip = ImageClip(outro_image_path, duration=3)
        
        # Combine all clips
        all_clips = [intro_clip, artist_clip, artwork_clip] + point_clips + [outro_clip]
        final_clip = concatenate_videoclips(all_clips, method="compose")
        
        # Add background music (would normally use royalty-free music)
        # For demo purposes, we'll use a silent audio track
        final_clip = final_clip.without_audio()
        
        # Write the video file
        output_path = os.path.join(temp_dir, "art_journey.mp4")
        final_clip.write_videofile(output_path, fps=24, codec='libx264', 
                                audio_codec='aac', preset='medium')
        
        return output_path
    
    except Exception as e:
        # Capture the full traceback
        error_traceback = traceback.format_exc()
        # Print it to console
        print(f"Full error traceback:\n{error_traceback}")
        # You can also return it or store it
        return f"Error generating video: {str(e)}\n\nFull traceback:\n{error_traceback}"

def resize_array(array, new_size):
    
    # Convert numpy array to PIL Image
    img = Image.fromarray(array.astype('uint8'))
    
    # Resize the image
    resized_img = img.resize((new_size[0], new_size[1]), Image.LANCZOS)
    
    # Convert back to numpy array
    return np.array(resized_img)

# Function to create an image with text
def create_text_image(text, size, font_size, temp_dir, filename):
    # Create a new image with dark background
    width, height = size
    image = Image.new('RGB', (width, height), (33, 33, 33))
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("Arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    lines = text.split('\n')
    text_height = 0
    line_heights = []
    
    for line in lines:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        line_height = bottom - top
        text_height += line_height
        line_heights.append(line_height)
    
    y = (height - text_height) // 2
    
    # Draw each line centered
    for i, line in enumerate(lines):
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        line_width = right - left
        x = (width - line_width) // 2
        draw.text((x, y), line, font=font, fill="white")
        y += line_heights[i]
    
    # Save the image
    output_path = os.path.join(temp_dir, filename)
    image.save(output_path)
    
    return output_path

# Function to add text to an existing image
def add_text_to_image(image_path, text, temp_dir, filename):
    # Load the image
    img = Image.open(image_path)
    
    # Resize to ensure height is 1080
    img = img.convert('RGB')
    img = resize_image_to_height(img, 1080)
    
    # Center and crop if necessary
    if img.width > 1080:
        left = (img.width - 1080) // 2
        img = img.crop((left, 0, left + 1080, 1080))
    
    # Create a semi-transparent overlay for text background
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("Arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text dimensions for proper wrapping
    max_width = 900
    wrapped_text = wrap_text(text, font, max_width)
    
    # Get text dimensions
    left, top, right, bottom = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
    text_width = right - left
    text_height = bottom - top
    
    # Create background rectangle at bottom
    margin = 20
    rect_height = text_height + (margin * 2)
    rect_width = min(text_width + (margin * 2), img.width)
    rect_x = (img.width - rect_width) // 2
    rect_y = img.height - rect_height - margin
    
    # Draw semi-transparent background
    draw.rectangle(
        [rect_x, rect_y, rect_x + rect_width, rect_y + rect_height],
        fill=(0, 0, 0, 180)  # Black with 70% opacity
    )
    
    # Position text
    text_x = (img.width - text_width) // 2
    text_y = rect_y + margin
    
    # Draw text
    draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255, 255))
    
    # Composite the overlay with the original image
    img = img.convert('RGBA')
    result = Image.alpha_composite(img, overlay)
    result = result.convert('RGB')  # Convert back to RGB for saving
    
    # Save the image
    output_path = os.path.join(temp_dir, filename)
    result.save(output_path)
    
    return output_path

# Helper function to resize image to a specific height
def resize_image_to_height(image, target_height):
    width, height = image.size
    ratio = target_height / height
    new_width = int(width * ratio)
    return image.resize((new_width, target_height), Image.LANCZOS)

# Helper function to wrap text
def wrap_text(text, font, max_width):
    """Wrap text to fit within the specified width."""
    words = text.split()
    wrapped_lines = []
    current_line = []
    
    for word in words:
        # Add the word to the current line
        current_line.append(word)
        # Check if the line is now too wide
        line = ' '.join(current_line)
        left, top, right, bottom = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), line, font=font)
        line_width = right - left
        
        if line_width > max_width:
            # Remove the last word
            current_line.pop()
            # Add the current line to wrapped lines
            if current_line:
                wrapped_lines.append(' '.join(current_line))
            # Start a new line with the word that didn't fit
            current_line = [word]
    
    # Add the last line
    if current_line:
        wrapped_lines.append(' '.join(current_line))
    
    return '\n'.join(wrapped_lines)

# Function to generate artistic variations of the image (unchanged)
def generate_image_variations(img, temp_dir):
    variations = []
    
    # Variation 1: High contrast
    var1 = img.copy()
    enhancer = ImageEnhance.Contrast(var1)
    var1 = enhancer.enhance(1.5)
    var1 = var1.convert('RGB')
    var1_path = os.path.join(temp_dir, "var1.jpg")
    var1.save(var1_path)
    variations.append(var1_path)
    
    # Variation 2: Black and white
    var2 = img.copy().convert('L').convert('RGB')
    var2_path = os.path.join(temp_dir, "var2.jpg")
    var2.save(var2_path)
    variations.append(var2_path)
    
    # Variation 3: Focus on details (crop center and zoom)
    var3 = img.copy()
    width, height = var3.size
    crop_size = min(width, height) * 0.6
    left = (width - crop_size) / 2
    top = (height - crop_size) / 2
    right = (width + crop_size) / 2
    bottom = (height + crop_size) / 2
    var3 = var3.crop((left, top, right, bottom))
    var3 = var3.resize(img.size, Image.LANCZOS)
    var3 = var3.convert('RGB')
    var3_path = os.path.join(temp_dir, "var3.jpg")
    var3.save(var3_path)
    variations.append(var3_path)
    
    # Variation 4: Artistic filter (blur edge focus)
    var4 = img.copy()
    
    # Create a mask for the center focus
    width, height = var4.size
    mask = Image.new('L', var4.size, 0)
    draw = ImageDraw.Draw(mask)
    center_x, center_y = width / 2, height / 2
    max_radius = min(width, height) / 2
    
    # Draw gradient circle
    for i in range(int(max_radius), 0, -1):
        opacity = int(255 * (i / max_radius))
        draw.ellipse(
            (center_x - i, center_y - i, center_x + i, center_y + i),
            fill=opacity
        )
    
    # Apply blur based on mask
    blurred = var4.filter(ImageFilter.GaussianBlur(radius=10))
    var4 = Image.composite(var4, blurred, mask)
    
    var4 = var4.convert('RGB')
    var4_path = os.path.join(temp_dir, "var4.jpg")
    var4.save(var4_path)
    variations.append(var4_path)
    
    # Variation 5: Color accent (saturation adjustment)
    var5 = img.copy()
    enhancer = ImageEnhance.Color(var5)
    var5 = enhancer.enhance(1.8)
    var5 = var5.convert('RGB')
    var5_path = os.path.join(temp_dir, "var5.jpg")
    var5.save(var5_path)
    variations.append(var5_path)
    
    return variations

# Add this to main.py to integrate the video generation (unchanged)
def integrate_video_generation():

    # Add a new section in your UI for video generation
    if 'analysis_result' in st.session_state and st.session_state.analysis_result:
        st.header("🎬 Art Journey Video")
        with st.expander("Generate Video Presentation", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### Generate an engaging video about this artwork")
                st.markdown("""
                Our AI will create a video presentation that:
                - Highlights key aspects of the artwork
                - Provides visual focus on important details
                - Creates an engaging art education experience
                """)
                
                if st.button("Generate Art Journey Video"):
                    with st.spinner("Creating your video... This may take a minute or two."):
                        try:
                            # Get required data from session state
                            analysis = st.session_state.analysis_result
                            image_data = st.session_state.uploaded_image_data
                            artwork_type = st.session_state.artwork_type
                            artist = st.session_state.artist if 'artist' in st.session_state else "Unknown"
                            title = st.session_state.title if 'title' in st.session_state else "Unknown"
                            
                            # Generate the video
                            video_path = generate_art_video(
                                image_data,
                                analysis,
                                artwork_type,
                                artist,
                                title
                            )
                            
                            # Save the path to session state
                            st.session_state.video_path = video_path
                            st.session_state.video_generated = True
                            
                            st.success("Video generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating video: {e}")
                
            with col2:
                st.image("https://via.placeholder.com/300x300?text=Video+Preview", 
                         caption="AI Video Generation", use_container_width=True)
            
            # Display the video if it exists
            if 'video_generated' in st.session_state and st.session_state.video_generated:
                st.video(st.session_state.video_path)
                
                # Provide download button
                with open(st.session_state.video_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Video",
                        data=file,
                        file_name="art_journey.mp4",
                        mime="video/mp4"
                    )

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
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analysis", "🌐 Web Insights", "📈 Visualization", "🎥 AI Generated Video", "🔗 Resources"])
            
            with st.spinner("Analyzing artwork..."):
                # Classify artwork type
                artwork_type = classify_artwork_type(image_bytes)
                
                # Get the complete artwork analysis
                analysis = analyze_artwork(image_bytes, artwork_type)
                
                # Extract artist and title for further searches
                artist, title, search_terms = extract_artist_and_title(analysis)
                
                # Store key data in session state so all tabs can access it
                st.session_state.analysis_result = analysis
                st.session_state.uploaded_image_data = image_bytes
                st.session_state.artwork_type = artwork_type
                st.session_state.artist = artist
                st.session_state.title = title
                st.session_state.search_terms = search_terms
                
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

                # Tab 4: AI Generated Video
                with tab4:
                    st.header("🎬 Art Journey Video")
                    st.markdown("""
                    Transform this artwork into an engaging video presentation that highlights key artistic elements and tells its story.
                    
                    Our AI will:
                    - Create a professional video presentation about this artwork
                    - Highlight key aspects of the artistic style and technique
                    - Focus on important details through visual enhancements
                    - Add informative commentary based on the analysis
                    """)
                    

                    
                    # Check if video has already been generated in this session
                    if 'video_generated' not in st.session_state:
                        st.session_state.video_generated = False
                    
                    # Generate video button
                    if st.button("Generate Art Journey Video", key="gen_video_btn", type="primary"):
                        with st.spinner("Creating your video... This may take a minute or two."):
                            try:
                                # Make sure we have all required data
                                if 'uploaded_image_data' not in st.session_state:
                                    st.error("Please upload an artwork image first.")
                                elif 'analysis_result' not in st.session_state:
                                    st.error("Please analyze the artwork before generating a video.")
                                else:
                                    # Set default values if not present
                                    artwork_type = st.session_state.get('artwork_type', "artwork")
                                    artist = st.session_state.get('artist', "Unknown")
                                    title = st.session_state.get('title', "Unknown")
                                    
                                    # Generate the video using session state data
                                    video_path = generate_art_video(
                                        st.session_state.uploaded_image_data,
                                        st.session_state.analysis_result,
                                        artwork_type,
                                        artist,
                                        title
                                    )
                                    
                                    # Save the path to session state
                                    st.session_state.video_path = video_path
                                    st.session_state.video_generated = True
                                    
                                    st.success("Video generated successfully!")
                            except Exception as e:
                                st.error(f"Error generating video: {str(e)}")
                                # Show full traceback for debugging
                                st.exception(e)
                    
                    # Display the video if it exists
                    if st.session_state.video_generated and 'video_path' in st.session_state:
                        st.subheader("Your Art Journey Video")
                        st.video(st.session_state.video_path)
                        
                        # Provide download button in a cleaner layout
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            try:
                                with open(st.session_state.video_path, "rb") as file:
                                    btn = st.download_button(
                                        label="Download Video",
                                        data=file,
                                        file_name="art_journey.mp4",
                                        mime="video/mp4",
                                        use_container_width=True
                                    )
                            except Exception as e:
                                st.error(f"Error accessing video file: {str(e)}")
                        
                        # Add option to regenerate
                        st.markdown("---")
                        if st.button("Generate New Video", key="regen_video_btn"):
                            st.session_state.video_generated = False
                            st.rerun()
                
                # Tab 5: Resources
                with tab5:
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
