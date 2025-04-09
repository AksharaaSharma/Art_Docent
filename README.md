<div align="center">
  
# 🎨 DeepBrush 🖌️

### *Where AI Becomes the Artist's Companion*

[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Gemini AI](https://img.shields.io/badge/Powered%20by-Gemini%20AI-purple.svg)](https://gemini.google.com/)

Prototype Link: https://genta-prototype-by-akshara.streamlit.app/
---

</div>

<div align="center">
<i>DeepBrush is a virtual docent powered by artificial intelligence, offering profound insights into the world of art through advanced analysis and interpretation.</i>
</div>

## ✨ The Canvas of Possibilities

DeepBrush transforms how we perceive and understand artistic expression. Using Google's Gemini 1.5 models, it analyzes paintings, sculptures, drawings, and other art forms with the discerning eye of a seasoned art historian.

---

## 🖼️ Gallery of Features

### 🧠 Artwork Recognition
- **Intelligent Classification** — Distinguishes between paintings, sculptures, drawings, and other art forms
- **Swift Visual Processing** — Leverages Gemini 1.5 Flash for immediate artwork recognition

### 🔍 Artistic Interpretation
- **Comprehensive Analysis** powered by Gemini 1.5 Pro:
  - *Title & Artist Identification* — Unveils the creator behind the masterpiece
  - *Period & Style Classification* — Places the work in its historical context
  - *Visual Composition Analysis* — Deconstructs the artwork's visual elements
  - *Color Palette Extraction* — Identifies the artist's chromatic choices
  - *Contextual Interpretation* — Reveals the story and meaning behind the piece
  - *Artistic Lineage* — Connects the work to similar artistic expressions
  - *Technical Evaluation* — Examines the craftsmanship and techniques employed

### 📊 Visual Poetry in Data
- **Artistic Element Visualization**:
  - *Radar Charts* — Mapping the prominence of visual elements
  - *Color Spectrum Analysis* — Capturing the artwork's palette
  - *Emotional Resonance Mapping* — Charting the emotional landscape

### 🌐 Art Knowledge Networks
- **Intelligent Web Exploration**:
  - *Curated Resource Discovery* — Finds authoritative information about the artwork
  - *Museum Database Integration* — Connects with prestigious art institutions
  - *Wikipedia Knowledge Extraction* — Gathers contextual information
  - *Adaptability* — Handles both famous masterpieces and obscure works

---

## 🎭 The Artistic Journey

```
🖼️ Upload Artwork → 🔍 AI Analysis → 🧩 Element Extraction → 
🌐 Web Exploration → 📊 Visual Storytelling → 🔗 Curated Discoveries
```

---

## 💻 Behind the Masterpiece

```python
# The Art of Code: A Brief Glimpse

# Establish your connection to the creative AI
GEMINI_API_KEY = "your_api_key_here"
genai.configure(api_key=GEMINI_API_KEY)

# Begin the artistic journey
with open("artwork.jpg", "rb") as canvas:
    image_data = canvas.read()

# Discover the nature of the artwork
artwork_type = classify_artwork_type(image_data)

# Unveil the artwork's essence
analysis = analyze_artwork(image_data, artwork_type)

# Identify the creator and creation
artist, title, search_terms = extract_artist_and_title(analysis)

# Explore the broader artistic context
insights, search_query = scrape_art_insights(artist, title, search_terms)

# Visualize the artistic elements
fig, description = create_visualization(analysis, artwork_type)

# Open paths to further exploration
links, search_query = get_relevant_links(artist, title, search_terms)
```

---

## 🏛️ Applications in the Art World

- **Educational Renaissance** — Transform art education with detailed analysis
- **Museum Exploration** — Carry a personal art historian in your pocket
- **Artistic Research** — Accelerate understanding of unfamiliar artworks
- **Content Creation** — Generate rich, informed art commentary

---

## 📦 The Artist's Toolkit

- Python 3.7+
- Google Generative AI Python SDK
- Requests & Beautiful Soup 4
- Matplotlib & Seaborn
- Supporting libraries: Logging, JSON, Time, Random, Base64, Re

---

<div align="center">

## 🌟 *DeepBrush: Where Technology Meets Artistic Vision* 🌟

*Transforming pixels into insights, data into understanding, and AI into art appreciation*

</div>
