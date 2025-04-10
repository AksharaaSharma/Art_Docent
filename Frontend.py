def frontend():
    
    import streamlit as st

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
