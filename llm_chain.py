# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        # Using the direct model name to avoid 404 errors on Streamlit Cloud
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        # System Prompt contains {destination}, {budget}, {days}, {travel_type}, {interests}
        # Human Message uses {user_notes} to avoid naming collisions
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", VACATION_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_notes}") 
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests, chat_history):
        # Convert Streamlit session state (dicts) to LangChain Message objects
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        # Execute Chain
        # We map 'interests' (from app.py) to both the prompt variable and the human message
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "interests": interests,    # Fills {interests} in VACATION_PROMPT
            "user_notes": interests,   # Fills {user_notes} in the human template
            "chat_history": formatted_history
        })