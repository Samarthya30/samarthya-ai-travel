import streamlit as st
import os
import time
from dotenv import load_dotenv
from llm_chain import VacationPlanner

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Samarthya AI | Travel Architect",
    page_icon="🔥",
    layout="wide"
)

# --- 2. DYNAMIC BACKGROUND & PREMIUM CSS ---
def apply_styling(query=None):
    overlay = "rgba(14, 17, 23, 0.85)"
    bg_img = ""
    
    if query:
        # Using loremflickr for stable keyword-based images
        bg_url = f"https://loremflickr.com/1920/1080/{query},travel/all"
        bg_img = f'url("{bg_url}")'
    
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient({overlay}, {overlay}), {bg_img};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #FFFFFF;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .main-block {{ animation: fadeIn 1s ease-out; }}

        .brand-text {{
            font-family: 'Orbitron', sans-serif;
            color: #FF4B4B;
            font-size: 14px;
            letter-spacing: 5px;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .stButton>button {{
            background-color: #FF4B4B !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            transition: 0.3s;
            width: 100%;
        }}
        
        .stButton>button:hover {{
            transform: scale(1.02);
            box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
        }}

        section[data-testid="stSidebar"] {{
            background-color: #050505;
            border-right: 1px solid #FF4B4B;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- 3. INITIALIZATION & SESSION STATE ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("🔑 API Key missing!")
    st.stop()

planner = VacationPlanner(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

# --- 4. SIDEBAR & CONSOLIDATED INPUTS ---
with st.sidebar:
    st.markdown("<p class='brand-text'>SAMARTHYA KR.</p>", unsafe_allow_html=True)
    st.write("Next-Gen AI Travel Architect")
    st.divider()
    
    dest = st.text_input("🎯 DESTINATION", placeholder="e.g. Kyoto, Japan")
    budget = st.text_input("💳 BUDGET", placeholder="e.g. 4000 USD")
    days = st.number_input("⏱️ DURATION (DAYS)", 1, 30, 5)
    style = st.selectbox("🎭 TRIP STYLE", ["Adventure", "Relaxation", "Cultural", "Luxury Elite"])
    dietary = st.multiselect("🍴 DIETARY", ["Vegetarian", "Vegan", "Halal", "Street Food Lover"], default=[])
    
    # Combined field for initial interests and future edits
    user_input = st.text_area("🗒️ SPECIAL REQUIREMENTS / EDITS", 
                               placeholder="Initial: 'Vegan food, photography'\nFollow-up: 'Remove Day 2' or 'Add a museum'")
    
    st.write(" ")
    
    # SINGLE PRIMARY ACTION BUTTON
    if st.button("🚀 ARCHITECT ITINERARY"):
        if dest and budget:
            # Prepare contextual instructions
            dietary_str = f"Dietary: {', '.join(dietary)}." if dietary else ""
            instruction = f"{user_input}. {dietary_str}".strip()
            
            with st.spinner("⏳ Re-Engineering your blueprint..."):
                try:
                    # Generate response using memory
                    response = planner.generate_itinerary(dest, budget, days, style, instruction, st.session_state.messages)
                    
                    # Update History
                    st.session_state.messages.append({"role": "user", "content": instruction})
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"SYSTEM_ERR: {e}")
        else:
            st.warning("Please fill Destination and Budget.")

    if st.button("🗑️ RESET ENGINE"):
        st.session_state.messages = []
        st.rerun()

# Apply Dynamic Styling
apply_styling(dest if dest else "travel")

# --- 5. MAIN INTERFACE ---
st.markdown("<div class='main-block'>", unsafe_allow_html=True)
st.markdown("<p class='brand-text'>SAMARTHYA TRAVEL ENGINE</p>", unsafe_allow_html=True)
st.title("Bespoke AI Itinerary")

# --- 6. DISPLAY LOGIC ---
# Only show the latest itinerary to keep it clean, or show the whole chat history
if st.session_state.messages:
    # We display the last assistant response as the "Current Plan"
    latest_plan = [msg for msg in st.session_state.messages if msg["role"] == "assistant"][-1]["content"]
    
    with st.chat_message("assistant", avatar="🔴"):
        st.write_stream(stream_data(latest_plan))
    
    st.download_button("📩 DOWNLOAD CURRENT PLAN", latest_plan, file_name=f"{dest}_plan.txt")
else:
    st.info("👋 Enter your details in the sidebar and click 'ARCHITECT' to begin your journey.")

st.markdown("</div>", unsafe_allow_html=True)