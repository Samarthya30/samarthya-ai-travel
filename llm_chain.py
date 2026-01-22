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
            # CHANGE: Use {interests} here because it's already inside your VACATION_PROMPT
            ("human", "{interests}") 
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_itinerary(self, destination, budget, days, travel_type, interests, chat_history):
        formatted_history = []
        for msg in chat_history:
            # Fixing the class instantiation here as well
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            else:
                formatted_history.append(AIMessage(content=msg["content"]))

        # The keys here must match the {} placeholders in your prompt EXACTLY
        return self.chain.invoke({
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "interests": interests,  # This now matches the {interests} in the template
            "chat_history": formatted_history
        })