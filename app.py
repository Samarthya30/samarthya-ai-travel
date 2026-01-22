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

# --- 2. PREMIUM DARK & RED CSS ---
def apply_styling():
    st.markdown("""
        <style>
        /* Global Background: Deep Black & Subtle Red Radial Gradient */
        .stApp {
            background: radial-gradient(circle at top right, #2b0000, #050505 60%);
            background-color: #050505;
            color: #FFFFFF;
        }
        
        /* Glassmorphism Main Container */
        .main-block {
            background: rgba(15, 15, 15, 0.7);
            border: 1px solid rgba(255, 75, 75, 0.2);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
            margin-top: 20px;
            animation: fadeIn 1.2s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .brand-text {
            font-family: 'Orbitron', sans-serif;
            color: #FF4B4B;
            font-size: 14px;
            letter-spacing: 6px;
            font-weight: bold;
            text-transform: uppercase;
            text-shadow: 0 0 15px rgba(255, 75, 75, 0.5);
        }

        /* Neon Red Primary Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #8b0000, #FF4B4B) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            height: 48px !important;
            font-weight: bold !important;
            letter-spacing: 1.5px !important;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
            transition: 0.4s all ease;
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(255, 75, 75, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        /* Sidebar Customization */
        section[data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 1px solid #FF4B4B;
        }

        /* Input Field Styling */
        input, textarea, .stSelectbox {
            background-color: #121212 !important;
            color: white !important;
            border-radius: 8px !important;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #FF4B4B; border-radius: 10px; }
        </style>
        """, unsafe_allow_html=True)

# --- 3. INITIALIZATION ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("🔑 API Key missing! Check your environment variables.")
    st.stop()

planner = VacationPlanner(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

# --- 4. SIDEBAR LOGIC ---
apply_styling()

with st.sidebar:
    st.markdown("<p class='brand-text'>SAMARTHYA KR.</p>", unsafe_allow_html=True)
    st.write("Next-Gen AI Travel Architect")
    st.divider()
    
    dest = st.text_input("🎯 TARGET DESTINATION", placeholder="e.g. Paris, France")
    budget = st.text_input("💳 TOTAL BUDGET", placeholder="e.g. 5000 USD")
    days = st.number_input("⏱️ DURATION (DAYS)", 1, 30, 5)
    style = st.selectbox("🎭 TRIP STYLE", ["Adventure", "Relaxation", "Cultural", "Luxury Elite"])
    dietary = st.multiselect("🍴 DIETARY", ["Vegetarian", "Vegan", "Halal", "Gluten-Free"], default=[])
    
    # This is the "Brain" of the conversation
    user_notes = st.text_area("🗒️ SPECIAL REQUIREMENTS / EDITS", 
                               placeholder="Example: 'Vegan food only' or 'Make Day 2 more relaxed' or 'Extend to 7 days'",
                               height=150)
    
    st.write(" ")
    
    if st.button("🚀 ARCHITECT ITINERARY"):
        if dest and budget:
            # Consolidate dietary and notes for the LLM
            diet_info = f"Dietary: {', '.join(dietary)}." if dietary else ""
            full_instruction = f"{user_notes} {diet_info}".strip()
            
            with st.spinner("⏳ Re-Engineering your blueprint..."):
                try:
                    # Logic: Passes everything to the chain, including current chat history
                    response = planner.generate_itinerary(
                        dest, budget, days, style, full_instruction, st.session_state.messages
                    )
                    
                    # Update Session History
                    st.session_state.messages.append({"role": "user", "content": full_instruction})
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"ENGINE_ERR: {str(e)}")
        else:
            st.warning("Destination and Budget are required to begin.")

    if st.button("🗑️ RESET SYSTEM"):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN DISPLAY ---
st.markdown("<div class='main-block'>", unsafe_allow_html=True)
st.markdown("<p class='brand-text'>SAMARTHYA TRAVEL ENGINE</p>", unsafe_allow_html=True)
st.title("Bespoke AI Architecture")

if st.session_state.messages:
    # Always grab the most recent assistant response for display
    # This ensures edits appear as the "new" single plan
    latest_plan = [msg for msg in st.session_state.messages if msg["role"] == "assistant"][-1]["content"]
    
    with st.chat_message("assistant", avatar="🔴"):
        st.write_stream(stream_data(latest_plan))
    
    st.write("---")
    st.download_button(
        label="📩 DOWNLOAD ARCHITECTURAL PLAN",
        data=latest_plan,
        file_name=f"Samarthya_{dest}_Plan.txt",
        mime="text/plain"
    )
else:
    st.info("👋 Enter your travel parameters in the sidebar and click **ARCHITECT** to generate your bespoke plan.")

st.markdown("</div>", unsafe_allow_html=True)