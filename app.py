import streamlit as st
import os
import time
from dotenv import load_dotenv
from llm_chain import VacationPlanner

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Samarthya AI | Travel",
    page_icon="🔥",
    layout="wide"
)

# --- 2. SAMARTHYA DARK & RED THEME CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-block { animation: fadeIn 1.5s ease-out; }

    .brand-text {
        font-family: 'Orbitron', sans-serif;
        color: #FF4B4B;
        font-size: 14px;
        letter-spacing: 5px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: -10px;
    }

    /* Red Pulsing Button */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(255, 75, 75, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }

    .stButton>button {
        background-color: #FF4B4B !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.6rem 2rem !important;
        font-weight: bold !important;
        animation: pulse 2s infinite;
        width: 100%;
    }

    section[data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

# --- 4. INITIALIZATION ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("🔑 API Key missing!")
    st.stop()

planner = VacationPlanner(api_key)

# --- 5. MAIN UI LAYOUT ---
st.markdown("<div class='main-block'>", unsafe_allow_html=True)

# Top Branding
st.markdown("<p class='brand-text'>SAMARTHYA VACATION PLANNER</p>", unsafe_allow_html=True)
st.title("Travel With Me")
st.write("---")

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color:#FF4B4B;'>SAMARTHYA KR.</h2>", unsafe_allow_html=True)
    st.write("Pushing the boundaries of generative intelligence.")
    st.divider()
    st.caption("Model: Gemini 2.5 Flash")

# --- INPUT SECTION ---
c1, c2 = st.columns(2)

with c1:
    dest = st.text_input("🎯 TARGET DESTINATION", placeholder="e.g. Dubai, UAE")
    budget = st.text_input("💳 BUDGET ALLOCATION", placeholder="e.g. 5000 USD")

with c2:
    days = st.number_input("⏱️ DURATION (DAYS)", min_value=1, max_value=30, value=5)
    style = st.selectbox("🎭 TRIP ARCHITECTURE", ["High-Octane Adventure", "Minimalist Relaxation", "Cultural Immersion", "Luxury Elite"])

# --- NEW: USER FRIENDLY QUESTIONS ---
st.markdown("<h4 style='color:#FF4B4B;'>🍕 CULINARY & LIFESTYLE PREFERENCES</h4>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)

with col_a:
    dietary = st.multiselect("Dietary Choices", ["No Preference", "Vegetarian", "Vegan", "Halal", "Gluten-Free"], default="No Preference")
with col_b:
    pace = st.select_slider("Trip Pace", options=["Chill", "Balanced", "Fast-Paced"], value="Balanced")

interests = st.text_area("🗒️ SPECIAL REQUIREMENTS / INTERESTS", placeholder="e.g. Photography, hidden speakeasies, tech hubs...")

# --- EXECUTION ---
if st.button("GENERATE ITINERARY"):
    if dest and budget:
        # Combine the new fields into the 'interests' string for the LLM
        refined_interests = f"Interests: {interests}. Dietary: {', '.join(dietary)}. Pace: {pace}."
        
        with st.spinner("⏳ ARCHITECTING YOUR JOURNEY..."):
            try:
                # We pass the refined_interests which now contains the food & pace info
                itinerary = planner.generate_itinerary(dest, budget, days, style, refined_interests)
                
                st.markdown("<h3 style='color:#FF4B4B;'>G.E.N.E.R.A.T.E.D  P.L.A.N</h3>", unsafe_allow_html=True)
                
                with st.chat_message("assistant", avatar="🔴"):
                    st.write_stream(stream_data(itinerary))
                
                st.download_button("DOWNLOAD ITINERARY", itinerary, file_name=f"{dest}_plan.txt")
                
            except Exception as e:
                st.error(f"SYSTEM_ERR: {e}")
    else:
        st.warning("INPUT_ERR: Destination and Budget are mandatory.")

st.markdown("</div>", unsafe_allow_html=True)