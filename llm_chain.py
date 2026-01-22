# llm_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from prompts import VACATION_PROMPT

class VacationPlanner:
    def __init__(self, api_key):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", VACATION_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            # FIX: Rename this to 'user_notes' to avoid name collision with {interests}
            ("human", "{user_notes}") 
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests, chat_history):
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        # FIX: We now provide BOTH 'interests' for the prompt and 'user_notes' for the human chat
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "interests": interests,    # This fills {interests} in VACATION_PROMPT
            "user_notes": interests,   # This fills {user_notes} in the human message
            "chat_history": formatted_history
        })