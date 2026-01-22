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
    # Default overlay to ensure text readability
    overlay = "rgba(14, 17, 23, 0.85)"
    bg_img = ""
    
    if query:
        # Using a reliable high-res source for destination images
        bg_url = f"https://images.unsplash.com/photo-1500835595547-751c6606a0cc?auto=format&fit=crop&q=80&w=2000" # Fallback
        # Unsplash Source is deprecated; we use the keyword-based redirect or a placeholder
        bg_url = f"https://loremflickr.com/1920/1080/{query},landmark/all"
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
    st.error("🔑 API Key missing! Set it in your .env or Streamlit Secrets.")
    st.stop()

planner = VacationPlanner(api_key)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

# --- 4. SIDEBAR & INPUTS ---
with st.sidebar:
    st.markdown("<p class='brand-text'>SAMARTHYA KR.</p>", unsafe_allow_html=True)
    st.write("Next-Gen AI Travel Architect")
    st.divider()
    
    dest = st.text_input("🎯 TARGET DESTINATION", placeholder="e.g. Kyoto, Japan")
    budget = st.text_input("💳 BUDGET", placeholder="e.g. 4000 USD")
    days = st.number_input("⏱️ DURATION (DAYS)", 1, 30, 5)
    style = st.selectbox("🎭 TRIP STYLE", ["Adventure", "Relaxation", "Cultural", "Luxury Elite"])
    dietary = st.multiselect("🍴 DIETARY", ["Vegetarian", "Vegan", "Halal", "Street Food Lover"], default=[])
    
    col1, col2 = st.columns(2)
    with col1:
        generate_btn = st.button("🚀 ARCHITECT")
    with col2:
        if st.button("🗑️ CLEAR"):
            st.session_state.messages = []
            st.rerun()
            
    if generate_btn:
        if dest and budget:
            st.session_state.messages = [] # Reset for new initial plan
            refined_interests = f"Style: {style}. Dietary: {', '.join(dietary)}."
            
            with st.spinner("Constructing Initial Blueprint..."):
                # Pass history (currently empty) to the stateful planner
                initial_itinerary = planner.generate_itinerary(dest, budget, days, style, refined_interests, st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": initial_itinerary})
        else:
            st.warning("Input required: Destination & Budget.")

# Apply dynamic background
apply_styling(dest if dest else "travel")

# --- 5. MAIN CHAT INTERFACE ---
st.markdown("<div class='main-block'>", unsafe_allow_html=True)
st.markdown("<p class='brand-text'>SAMARTHYA TRAVEL ENGINE</p>", unsafe_allow_html=True)
st.title("Bespoke AI Itinerary")

# Display the conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🔴" if message["role"]=="assistant" else None):
        st.markdown(message["content"])

# Chat Input for Refinement (The "Continuous Chat" part)
if chat_input := st.chat_input("Suggest edits... (e.g. 'Add more local food' or 'Remove the museum visit')"):
    # Add User message to state
    st.session_state.messages.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)
    
    # Generate Stateful Output
    with st.chat_message("assistant", avatar="🔴"):
        with st.spinner("Modifying Architecture..."):
            # We pass the current chat_input as the 'interests' and send the whole message history
            # The memory logic in llm_chain.py will handle the rest!
            response = planner.generate_itinerary(dest, budget, days, style, f"REVISE: {chat_input}", st.session_state.messages)
            st.write_stream(stream_data(response))
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("</div>", unsafe_allow_html=True)