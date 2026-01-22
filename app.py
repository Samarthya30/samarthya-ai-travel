import streamlit as st
import os
from dotenv import load_dotenv
from llm_chain import VacationPlanner
from fpdf import FPDF

# --- INITIAL CONFIG ---
load_dotenv()
st.set_page_config(page_title="Samarthya AI | Travel Architect", page_icon="🧳", layout="wide")

# --- LUXURY CSS STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #1a0000, #000000 80%);
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #FF4B4B;
    }
    h1, h2, h3 {
        color: #FF4B4B !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    strong, b { color: #FF4B4B !important; }
    .stButton>button {
        background: linear-gradient(135deg, #8b0000 0%, #FF4B4B 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR (UPDATED FIX) ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    
    # FIX: Explicitly cast bytearray to bytes
    return bytes(pdf.output())

# --- INITIALIZATION ---
api_key = os.getenv("GOOGLE_API_KEY")
planner = VacationPlanner(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("<h1>SAMARTHYA AI</h1>", unsafe_allow_html=True)
    st.markdown("### ARCHITECT PARAMETERS")
    
    dest = st.text_input("📍 DESTINATION", "Tokyo, Japan")
    days = st.number_input("⏱️ DURATION (DAYS)", 1, 30, 5)
    budget = st.text_input("💳 BUDGET", "3000 USD")
    month = st.selectbox("📅 TRAVEL MONTH", 
                        ["January", "February", "March", "April", "May", "June", 
                         "July", "August", "September", "October", "November", "December"])
    diet = st.radio("🍴 DIETARY PREFERENCE", ["Veg", "Non-Veg", "Vegan"])
    style = st.selectbox("🎭 TRAVEL STYLE", ["Luxury Elite", "Adventure", "Cultural", "Relaxed"])

    if st.button("🚀 GENERATE ITINERARY"):
        with st.spinner("Designing your journey..."):
            res = planner.generate_itinerary(
                dest, budget, days, style, "Initial Build", month, diet, []
            )
            st.session_state.messages = [
                {"role": "user", "content": f"Architect a plan for {dest} in {month}"},
                {"role": "assistant", "content": res}
            ]

    if st.button("🗑️ RESET ENGINE"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN WORKSPACE ---
st.title("Travel Planning Engine")

for message in st.session_state.messages:
    avatar = "🔴" if message["role"] == "assistant" else "⚪"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if st.session_state.messages:
    st.divider()
    current_plan = st.session_state.messages[-1]["content"]
    
    try:
        # Generate the bytes-safe PDF
        pdf_bytes = create_pdf(current_plan)
        
        st.download_button(
            label="📥 DOWNLOAD FINAL ARCHITECTURE (PDF)",
            data=pdf_bytes,
            file_name=f"Samarthya_{dest}_Plan.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF Prep Error: {e}")

    if prompt := st.chat_input("Revision: (e.g., 'Remove restaurants')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="⚪"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🔴"):
            with st.spinner("Re-architecting..."):
                response = planner.generate_itinerary(
                    dest, budget, days, style, prompt, month, diet, st.session_state.messages[:-1]
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()