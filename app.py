import streamlit as st
import os
import time
from dotenv import load_dotenv
from llm_chain import VacationPlanner

# --------------------------------------------------
# 1. PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Samarthya AI | Travel Architect",
    page_icon="🔥",
    layout="wide"
)

# --------------------------------------------------
# 2. STYLING
# --------------------------------------------------
def apply_styling():
    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at top right, #2b0000, #050505 60%);
            color: #FFFFFF;
        }

        .main-block {
            background: rgba(15, 15, 15, 0.7);
            border: 1px solid rgba(255, 75, 75, 0.2);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            animation: fadeIn 1s ease-out;
        }

        .brand-text {
            text-align: center;
            font-size: 14px;
            letter-spacing: 6px;
            color: #FF4B4B;
            font-weight: bold;
        }

        .stButton>button {
            background: linear-gradient(90deg, #8b0000, #FF4B4B) !important;
            color: white !important;
            border-radius: 10px !important;
            height: 48px !important;
            font-weight: bold;
            width: 100%;
        }

        section[data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 1px solid #FF4B4B;
        }

        input, textarea, [data-baseweb="select"] {
            background-color: #121212 !important;
            color: white !important;
        }

        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(15px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 3. INIT
# --------------------------------------------------
apply_styling()
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("🔑 GOOGLE_API_KEY missing")
    st.stop()

planner = VacationPlanner(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def fake_stream(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.01)

# --------------------------------------------------
# 4. SIDEBAR INPUTS
# --------------------------------------------------
with st.sidebar:
    st.markdown("<p class='brand-text'>SAMARTHYA KR.</p>", unsafe_allow_html=True)
    st.write("Next-Gen AI Travel Architect")
    st.divider()

    destination = st.text_input("🎯 DESTINATION", placeholder="Paris, France")
    budget = st.text_input("💳 BUDGET", placeholder="5000 USD")
    days = st.number_input("⏱️ DAYS", min_value=1, max_value=30, value=5)
    travel_style = st.selectbox(
        "🎭 TRAVEL STYLE",
        ["Adventure", "Relaxation", "Cultural", "Luxury Elite"]
    )
    dietary = st.multiselect(
        "🍴 DIETARY",
        ["Vegetarian", "Vegan", "Halal", "Gluten-Free"]
    )

    user_notes = st.text_area(
        "🗒️ SPECIAL REQUESTS",
        placeholder="Example: Vegan food only, slow pace on Day 2",
        height=140
    )

    if st.button("🚀 ARCHITECT ITINERARY"):
        if not destination or not budget:
            st.warning("Destination and budget are required.")
        else:
            dietary_info = f"Dietary preferences: {', '.join(dietary)}." if dietary else ""
            final_notes = f"{user_notes}\n{dietary_info}".strip()

            with st.spinner("⏳ Designing your journey..."):
                try:
                    response = planner.generate_itinerary(
                        destination=destination,
                        budget=budget,
                        days=days,
                        travel_type=travel_style,
                        interests=final_notes,
                        chat_history=st.session_state.messages
                    )

                    st.session_state.messages.append({
                        "role": "user",
                        "content": final_notes
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    st.error(f"ENGINE_ERR: {e}")

    if st.button("🗑️ RESET"):
        st.session_state.messages = []
        st.rerun()

# --------------------------------------------------
# 5. MAIN OUTPUT
# --------------------------------------------------
st.markdown("<p class='brand-text'>SAMARTHYA TRAVEL ENGINE</p>", unsafe_allow_html=True)
st.markdown("<div class='main-block'>", unsafe_allow_html=True)

st.title("Bespoke AI Architecture")

if st.session_state.messages:
    last_answer = [m for m in st.session_state.messages if m["role"] == "assistant"][-1]["content"]

    with st.chat_message("assistant", avatar="🔴"):
        st.write_stream(fake_stream(last_answer))

    st.divider()
    st.download_button(
        "📩 DOWNLOAD PLAN",
        data=last_answer,
        file_name=f"{destination}_Travel_Plan.txt",
        mime="text/plain"
    )
else:
    st.info("👈 Enter details in the sidebar and click **ARCHITECT ITINERARY**")

st.markdown("</div>", unsafe_allow_html=True)