# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        # We use 'gemini-1.5-flash' which is the stable production ID.
        # Ensure your requirements.txt has: langchain-google-genai>=2.0.0
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=api_key,
            temperature=0.7,
            # This ensures the model uses the correct API version internally
            convert_system_message_to_human=True 
        )
        
        # System Prompt contains {destination}, {budget}, {days}, {travel_type}, {interests}
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
            elif msg["role"] == "assistant":
                formatted_history.append(AIMessage(content=msg["content"]))

        # Execute Chain
        # Mapping 'interests' to both the logic block and the current human query
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "interests": interests,    # For the logic in the system prompt
            "user_notes": interests,   # For the latest user request
            "chat_history": formatted_history
        })